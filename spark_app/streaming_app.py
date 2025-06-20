# spark_app/streaming_app.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, lit, sum as pyspark_sum, coalesce, when, udf
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, IntegerType, ArrayType,
    BooleanType, DoubleType
)
from pyspark.ml.feature import VectorAssembler
import os
import json
import time
import random

# --- Configuration ---
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:29092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')

# NEW: Cassandra Configuration
CASSANDRA_HOST = os.environ.get('CASSANDRA_HOST', 'cassandra')
CASSANDRA_KEYSPACE = os.environ.get('CASSANDRA_KEYSPACE', 'synapse_lite_ks')
CASSANDRA_TABLE = os.environ.get('CASSANDRA_TABLE', 'alerts')

# Define the schema for the incoming Bitcoin transaction JSON payload
transaction_schema = StructType([
    StructField("lock_time", LongType(), True),
    StructField("ver", IntegerType(), True),
    StructField("size", IntegerType(), True),
    StructField("inputs", ArrayType(
        StructType([
            StructField("sequence", LongType(), True),
            StructField("prev_out", StructType([
                StructField("spent", BooleanType(), True),
                StructField("tx_index", LongType(), True),
                StructField("type", IntegerType(), True),
                StructField("addr", StringType(), True),
                StructField("value", LongType(), True),
                StructField("n", IntegerType(), True),
                StructField("script", StringType(), True)
            ]), True),
            StructField("script", StringType(), True)
        ])
    ), True),
    StructField("time", LongType(), True),
    StructField("tx_index", LongType(), True),
    StructField("vin_sz", IntegerType(), True),
    StructField("hash", StringType(), True),
    StructField("vout_sz", IntegerType(), True),
    StructField("relayed_by", StringType(), True),
    StructField("out", ArrayType(
        StructType([
            StructField("spent", BooleanType(), True),
            StructField("tx_index", LongType(), True),
            StructField("type", IntegerType(), True),
            StructField("addr", StringType(), True),
            StructField("value", LongType(), True),
            StructField("n", IntegerType(), True),
            StructField("script", StringType(), True)
        ])
    ), True),
    StructField("producer_timestamp_ms", LongType(), True)
])


# Initialize Spark Session
spark = SparkSession.builder \
    .appName("BitcoinMempoolFraudDetection") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0") \
    .config("spark.sql.shuffle.partitions", "2") \
    .config("spark.cassandra.connection.host", CASSANDRA_HOST) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print(f"Spark Session initialized. Connecting to Kafka: {KAFKA_BROKER}, Topic: {KAFKA_TOPIC}")
print(f"Configured to write alerts to Cassandra: {CASSANDRA_HOST}/{CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE}")


# --- Read Stream from Kafka ---
df_transactions = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

# Parse the JSON value from Kafka using the defined schema
parsed_transactions = df_transactions.selectExpr("CAST(value AS STRING) as json_value") \
    .select(from_json(col("json_value"), transaction_schema).alias("data")) \
    .select("data.*")

# Add a processing time timestamp for windowing operations (using producer_timestamp_ms)
parsed_transactions = parsed_transactions.withColumn("processing_time", (col("producer_timestamp_ms") / 1000).cast("timestamp"))


# --- Feature Engineering ---
def sum_array_elements(arr):
    if arr is None:
        return 0
    total = 0
    for val in arr:
        if val is not None:
            total += val
    return total

sum_array_elements_udf = udf(sum_array_elements, LongType())


total_input_values_agg = parsed_transactions.withColumn(
    "total_input_value",
    sum_array_elements_udf(col("inputs.prev_out.value"))
)

total_output_values_agg = total_input_values_agg.withColumn(
    "total_output_value",
    sum_array_elements_udf(col("out.value"))
)

features_df = total_output_values_agg.withColumn(
    "transaction_fee",
    (col("total_input_value") - col("total_output_value")).cast(LongType())
)

features_df = features_df.withColumn(
    "fee_per_byte",
    when(col("size") > 0, col("transaction_fee").cast(DoubleType()) / col("size")).otherwise(0.0)
)

features_df = features_df.withColumn("num_inputs", col("vin_sz"))
features_df = features_df.withColumn("num_outputs", col("vout_sz"))

features_df = features_df.withColumn("feature_total_input_value", col("total_input_value").cast(DoubleType()))
features_df = features_df.withColumn("feature_transaction_fee", col("transaction_fee").cast(DoubleType()))
features_df = features_df.withColumn("feature_fee_per_byte", col("fee_per_byte"))
features_df = features_df.withColumn("feature_num_inputs", col("num_inputs").cast(DoubleType()))
features_df = features_df.withColumn("feature_num_outputs", col("num_outputs").cast(DoubleType()))


# --- ML Model Loading and Scoring (Dummy) ---
try:
    print("Simulating ML Model Scoring with Bitcoin transaction features...")

    feature_columns = [
        "feature_total_input_value",
        "feature_transaction_fee",
        "feature_fee_per_byte",
        "feature_num_inputs",
        "feature_num_outputs"
    ]
    assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
    ml_input_df = assembler.transform(features_df)

    ml_scored_df = ml_input_df.withColumn(
        "ml_fraud_score",
        when((col("feature_fee_per_byte") < 100) & (col("feature_num_outputs") > 5), 0.90)
        .when((col("feature_transaction_fee") < 1000) & (col("feature_total_input_value") > 1000000000), 0.85)
        .otherwise(random.uniform(0.01, 0.3))
    )
    print("ML Model Scoring simulated.")
except Exception as e:
    print(f"Error simulating ML model: {e}. Proceeding without ML scoring for now.")
    ml_scored_df = features_df.withColumn("ml_fraud_score", lit(0.0).cast(DoubleType()))


# --- Smurfing/Suspicious Pattern Detection (Rule-based for Demo) ---
suspicious_outputs_threshold = 5
small_value_per_output_threshold = 50000

smurfing_detected_df = ml_scored_df.withColumn(
    "is_smurfing_rule",
    when(
        (col("num_outputs") > suspicious_outputs_threshold) &
        (col("total_output_value") / col("num_outputs") < small_value_per_output_threshold),
        True
    ).otherwise(False)
)
print("Smurfing/Suspicious pattern detection rules applied.")

# --- Combine Flags and Generate Alerts ---
alerts_df = smurfing_detected_df.withColumn(
    "is_alert",
    (col("ml_fraud_score") > 0.8) | col("is_smurfing_rule")
)

final_alerts = alerts_df.filter(col("is_alert")).select(
    col("hash").alias("transaction_hash"),
    col("size"),
    col("time").alias("transaction_timestamp"),
    col("vin_sz").alias("num_inputs"),
    col("vout_sz").alias("num_outputs"),
    col("total_input_value"),
    col("total_output_value"),
    col("transaction_fee"),
    col("fee_per_byte"),
    col("ml_fraud_score"),
    col("is_smurfing_rule"),
    lit(int(time.time() * 1000)).alias("alert_timestamp_ms")
)

# --- SHAP Explanation (Simulated/Placeholder) ---
def get_shap_features(ml_score, fee_per_byte, num_outputs, is_smurfing):
    features = []
    if is_smurfing:
        features.append({"name": "HighNumberOfOutputs", "contribution": 0.4})
        features.append({"name": "LowValuePerOutput", "contribution": 0.3})
    elif ml_score > 0.8:
        if fee_per_byte < 100:
            features.append({"name": "VeryLowFeePerByte", "contribution": 0.5})
        elif num_outputs > 5:
            features.append({"name": "ManyOutputsMLTrigger", "contribution": 0.4})
        else:
            features.append({"name": "UnusualMLPattern", "contribution": 0.6})
    else:
        features.append({"name": "TransactionFee", "contribution": round(random.uniform(0.1, 0.6), 2)})
        features.append({"name": "TransactionSize", "contribution": round(random.uniform(0.05, 0.3), 2)})

    features_sorted = sorted(features, key=lambda x: x['contribution'], reverse=True)[:3]
    return json.dumps(features_sorted)

get_shap_features_udf = udf(get_shap_features, StringType())


final_alerts_with_shap = final_alerts.withColumn(
    "shap_features_json",
    get_shap_features_udf(
        col("ml_fraud_score"),
        col("fee_per_byte"),
        col("num_outputs"),
        col("is_smurfing_rule")
    )
)


# --- Write Alerts to Cassandra ---
query = final_alerts_with_shap.writeStream \
    .outputMode("append") \
    .format("org.apache.spark.sql.cassandra") \
    .option("checkpointLocation", "/opt/bitnami/spark/checkpoint") \
    .option("keyspace", CASSANDRA_KEYSPACE) \
    .option("table", CASSANDRA_TABLE) \
    .trigger(processingTime="5 seconds") \
    .start()

print(f"Spark Streaming query started, writing to Cassandra {CASSANDRA_KEYSPACE}.{CASSANDRA_TABLE}.")
print("Waiting for stream to terminate...")

query.awaitTermination()
print("Spark Streaming query terminated.")