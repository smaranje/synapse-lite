# spark_app/streaming_app.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, lit, sum as pyspark_sum, coalesce, when
from pyspark.sql.types import (
    StructType, StructField, StringType, LongType, IntegerType, ArrayType,
    BooleanType, DoubleType
)
from pyspark.ml.feature import VectorAssembler
# No LogisticRegressionModel import needed if not actually loading a model
# from pyspark.ml.classification import LogisticRegressionModel
import os
import json
import time
import random # Added for simulating feature generation and scores

# --- Configuration ---
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:29092') # From docker-compose env
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')

# Define the schema for the incoming Bitcoin transaction JSON payload
# This schema accurately reflects the structure provided from your bitcoin_mempool_consumer.py
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
                StructField("type", IntegerType(), True), # 'type' can be null
                StructField("addr", StringType(), True), # 'addr' can be null for some types
                StructField("value", LongType(), True),
                StructField("n", IntegerType(), True),
                StructField("script", StringType(), True)
            ]), True),
            StructField("script", StringType(), True)
        ])
    ), True),
    StructField("time", LongType(), True),
    StructField("tx_index", LongType(), True),
    StructField("vin_sz", IntegerType(), True), # Number of inputs
    StructField("hash", StringType(), True), # Transaction hash
    StructField("vout_sz", IntegerType(), True), # Number of outputs
    StructField("relayed_by", StringType(), True),
    StructField("out", ArrayType(
        StructType([
            StructField("spent", BooleanType(), True),
            StructField("tx_index", LongType(), True),
            StructField("type", IntegerType(), True), # 'type' can be null
            StructField("addr", StringType(), True), # 'addr' can be null for some types
            StructField("value", LongType(), True),
            StructField("n", IntegerType(), True),
            StructField("script", StringType(), True)
        ])
    ), True),
    # This is the custom timestamp added by your consumer script
    StructField("producer_timestamp_ms", LongType(), True)
])


# Initialize Spark Session
# Using 'spark-master' as the master address, as defined in docker-compose.yml
spark = SparkSession.builder \
    .appName("BitcoinMempoolFraudDetection") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.sql.shuffle.partitions", "2") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN") # Reduce verbosity of Spark logs

print(f"Spark Session initialized. Connecting to Kafka: {KAFKA_BROKER}, Topic: {KAFKA_TOPIC}")

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
    .select("data.*") # Select all fields from the parsed 'data' struct

# Add a processing time timestamp for windowing operations (using producer_timestamp_ms)
parsed_transactions = parsed_transactions.withColumn("processing_time", (col("producer_timestamp_ms") / 1000).cast("timestamp"))


# --- Feature Engineering ---
# Calculate total input value by summing 'value' from all 'prev_out' in 'inputs'
# Explode the inputs array to sum values, then group back by transaction hash
# Use coalesce to handle cases where sum might be null (e.g., if inputs array is empty)
total_input_value_df = parsed_transactions \
    .withColumn("input_exploded", col("inputs")) \
    .withColumn("prev_out_value", col("input_exploded.prev_out.value")) \
    .select(col("hash"), col("prev_out_value"))

# We need to handle the array of values from prev_out.value and sum them up
# This requires a UDF or more complex Spark SQL array functions
# Let's flatten the array of arrays and sum
def sum_array_elements(arr):
    if arr is None:
        return 0
    total = 0
    for inner_arr in arr:
        if inner_arr is not None:
            for val in inner_arr:
                if val is not None:
                    total += val
    return total

sum_array_elements_udf = spark.udf.register("sum_array_elements", sum_array_elements, LongType())


# Calculate total input value
# Use a custom UDF to sum values within the array of structs
# Note: col("inputs.prev_out.value") will give an array of LongType
# We need to filter out nulls if any, before summing
# For robustness, we will collect all prev_out values into a list and sum them
total_input_values_agg = parsed_transactions.withColumn(
    "total_input_value",
    sum_array_elements_udf(col("inputs.prev_out.value"))
)

# Calculate total output value
total_output_values_agg = total_input_values_agg.withColumn(
    "total_output_value",
    sum_array_elements_udf(col("out.value"))
)

# Calculate transaction fee
# Ensure values are not null before subtraction; default to 0 if null
features_df = total_output_values_agg.withColumn(
    "transaction_fee",
    (col("total_input_value") - col("total_output_value")).cast(LongType())
)

# Calculate fee per byte (handle division by zero for size)
features_df = features_df.withColumn(
    "fee_per_byte",
    when(col("size") > 0, col("transaction_fee").cast(DoubleType()) / col("size")).otherwise(0.0)
)

# Use vin_sz and vout_sz directly as features
features_df = features_df.withColumn("num_inputs", col("vin_sz"))
features_df = features_df.withColumn("num_outputs", col("vout_sz"))

# Renaming for consistency with 'feature_' prefix for ML input
features_df = features_df.withColumn("feature_total_input_value", col("total_input_value").cast(DoubleType()))
features_df = features_df.withColumn("feature_transaction_fee", col("transaction_fee").cast(DoubleType()))
features_df = features_df.withColumn("feature_fee_per_byte", col("fee_per_byte"))
features_df = features_df.withColumn("feature_num_inputs", col("num_inputs").cast(DoubleType()))
features_df = features_df.withColumn("feature_num_outputs", col("num_outputs").cast(DoubleType()))


# --- ML Model Loading and Scoring (Dummy) ---
try:
    print("Simulating ML Model Scoring with Bitcoin transaction features...")

    # Define the features to be used by the ML model
    feature_columns = [
        "feature_total_input_value",
        "feature_transaction_fee",
        "feature_fee_per_byte",
        "feature_num_inputs",
        "feature_num_outputs"
    ]
    assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
    ml_input_df = assembler.transform(features_df)

    # Simulate ML prediction:
    # A higher fraud score if fee_per_byte is very low, or if there's a large discrepancy
    # between input and output values relative to transaction size, or high num_outputs.
    ml_scored_df = ml_input_df.withColumn(
        "ml_fraud_score",
        when((col("feature_fee_per_byte") < 100) & (col("feature_num_outputs") > 5), 0.90) # Low fee/byte & many outputs
        .when((col("feature_transaction_fee") < 1000) & (col("feature_total_input_value") > 1000000000), 0.85) # Large input, small fee
        .otherwise(random.uniform(0.01, 0.3)) # Low score for normal txns
    )
    print("ML Model Scoring simulated.")
except Exception as e:
    print(f"Error simulating ML model: {e}. Proceeding without ML scoring for now.")
    # Default to a low score if ML simulation fails
    ml_scored_df = features_df.withColumn("ml_fraud_score", lit(0.0).cast(DoubleType()))


# --- Smurfing/Suspicious Pattern Detection (Rule-based for Demo) ---
# For Bitcoin mempool data, "smurfing" would typically involve complex graph analysis
# of address clusters. For this demo, we'll use a simpler rule based on available features:
# Flag transactions that have a high number of outputs with relatively small values
# (distributing funds to many addresses, potentially for layering).
suspicious_outputs_threshold = 5 # More than 5 outputs
small_value_per_output_threshold = 50000 # Average value per output < 0.0005 BTC (50,000 satoshis)

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
# An alert is generated if either the ML score is high or the smurfing/suspicious rule is triggered.
alerts_df = smurfing_detected_df.withColumn(
    "is_alert",
    (col("ml_fraud_score") > 0.8) | col("is_smurfing_rule")
)

# Select relevant columns for the alert
final_alerts = alerts_df.filter(col("is_alert")).select(
    col("hash").alias("transaction_hash"), # Use 'hash' as transaction_id
    col("size"),
    col("time").alias("transaction_timestamp"), # Original Bitcoin timestamp
    col("vin_sz").alias("num_inputs"),
    col("vout_sz").alias("num_outputs"),
    col("total_input_value"),
    col("total_output_value"),
    col("transaction_fee"),
    col("fee_per_byte"),
    col("ml_fraud_score"),
    col("is_smurfing_rule"),
    lit(int(time.time() * 1000)).alias("alert_timestamp_ms") # When alert was generated
)

# --- SHAP Explanation (Simulated/Placeholder) ---
# In a real system, SHAP would be calculated for high-risk transactions.
# For demo, we'll simulate top features based on the flags.
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

    # Sort by contribution and take top 3
    features_sorted = sorted(features, key=lambda x: x['contribution'], reverse=True)[:3]
    return json.dumps(features_sorted) # Return as JSON string

# Register the Python function as a UDF (User Defined Function)
spark.udf.register("get_shap_features_udf", get_shap_features, StringType())

final_alerts_with_shap = final_alerts.withColumn(
    "shap_features_json",
    # Pass the relevant columns as arguments to the UDF
    spark.udf.get_shap_features_udf(
        col("ml_fraud_score"),
        col("fee_per_byte"),
        col("num_outputs"),
        col("is_smurfing_rule")
    )
)


# --- Write Alerts (Currently to Console, later to Cassandra) ---
query = final_alerts_with_shap.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .trigger(processingTime="5 seconds") \
    .start()

print("Spark Streaming query started. Alerts will be printed to console.")
print("Waiting for stream to terminate...")

# Keep the Spark application running until terminated
query.awaitTermination()
print("Spark Streaming query terminated.")
