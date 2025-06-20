# spark_app/streaming_app.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, count, when, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, IntegerType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegressionModel
import os
import json
import time

# --- Configuration ---
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:29092') # From docker-compose env
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')

# Define schema for the incoming Kafka messages (transactions)
transaction_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("sender_account", StringType(), True),
    StructField("receiver_account", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("currency", StringType(), True),
    StructField("timestamp", LongType(), True),
    StructField("transaction_type", StringType(), True)
])

# Initialize Spark Session
# Using 'spark-master' as the master address, as defined in docker-compose.yml
spark = SparkSession.builder \
    .appName("SynapseLiteFraudDetection") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.sql.shuffle.partitions", "2") # Reduce partitions for small demo
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

# Parse the JSON value from Kafka
parsed_transactions = df_transactions.selectExpr("CAST(value AS STRING) as json_value") \
    .select(from_json(col("json_value"), transaction_schema).alias("data")) \
    .select("data.*")

# Add a processing time timestamp for windowing operations
parsed_transactions = parsed_transactions.withColumn("processing_time", col("timestamp").cast("timestamp"))


# --- Feature Engineering (Simple for Demo) ---
# Example: transaction amount, and potential future features
# For a real system, you'd calculate sender/receiver velocity, frequency, average amount, etc.
features_df = parsed_transactions.withColumn("feature_amount", col("amount"))
# Dummy features for ML model input later
features_df = features_df.withColumn("feature_tx_count_daily", lit(random.randint(1, 100)).cast(DoubleType()))
features_df = features_df.withColumn("feature_sender_avg_amt", lit(random.uniform(100.0, 10000.0)).cast(DoubleType()))


# --- ML Model Loading and Scoring (Dummy) ---
# In a real scenario, model.py would train and save a model.
# Here, we simulate a model application.
try:
    # Attempt to load a dummy model if it exists (e.g., from a prior run or build)
    # For a simple demo, we're not actually training/loading a model here,
    # but the structure shows where you would.
    # Replace with your actual model loading logic if you train one in model.py
    # and make it accessible (e.g., via mounted volume or Spark's distributed cache).
    print("Simulating ML Model Scoring...")
    # This is a dummy score. In reality, it would be from a loaded model.
    # Load a dummy ML model from model.py for actual inference
    # from model import load_dummy_model # Assuming model.py exposes a function
    # dummy_model = load_dummy_model()

    # Define the features to be used by the ML model
    feature_columns = ["feature_amount", "feature_tx_count_daily", "feature_sender_avg_amt"]
    assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
    ml_input_df = assembler.transform(features_df)

    # Simulate ML prediction: If amount is small and transaction type is transfer, higher fraud score
    ml_scored_df = ml_input_df.withColumn(
        "ml_fraud_score",
        when((col("amount") < 100) & (col("transaction_type") == "transfer"), 0.95)
        .otherwise(random.uniform(0.01, 0.3)) # Low score for normal txns
    )
    print("ML Model Scoring simulated.")
except Exception as e:
    print(f"Error simulating ML model: {e}. Proceeding without ML scoring for now.")
    ml_scored_df = features_df.withColumn("ml_fraud_score", lit(0.0).cast(DoubleType())) # Default if ML fails


# --- Smurfing Detection (Rule-based for Demo) ---
# Basic rule: Flag transactions if sender/receiver accounts are "smurfing accounts" and amount is low.
# This will be replaced by Neo4j graph analysis in a more advanced version.
smurfing_threshold_amount = 100.0
smurfing_keyword = "SMURF" # From how we generated synthetic data

smurfing_detected_df = ml_scored_df.withColumn(
    "is_smurfing_rule",
    when(
        (col("amount") < smurfing_threshold_amount) &
        (col("transaction_type") == "transfer") &
        ((col("sender_account").like(f"%{smurfing_keyword}%")) | (col("receiver_account").like(f"%{smurfing_keyword}%"))),
        True
    ).otherwise(False)
)
print("Smurfing detection rules applied.")

# --- Combine Flags and Generate Alerts ---
# An alert is generated if either the ML score is high or the smurfing rule is triggered.
alerts_df = smurfing_detected_df.withColumn(
    "is_alert",
    (col("ml_fraud_score") > 0.8) | col("is_smurfing_rule")
)

# Select relevant columns for the alert
final_alerts = alerts_df.filter(col("is_alert")).select(
    col("transaction_id"),
    col("sender_account"),
    col("receiver_account"),
    col("amount"),
    col("timestamp"),
    col("ml_fraud_score"),
    col("is_smurfing_rule"),
    lit(int(time.time() * 1000)).alias("alert_timestamp") # When alert was generated
)

# --- SHAP Explanation (Simulated/Placeholder) ---
# In a real system, SHAP would be calculated for high-risk transactions.
# For demo, we'll simulate top features.
def get_shap_features(score, amount, is_smurfing):
    # Dummy SHAP logic: amount is always a top feature.
    # If smurfing, then account types are important.
    # If high ML score, some other random feature might be important.
    features = []
    if amount < 200 and is_smurfing:
        features.append({"name": "LowAmount", "contribution": 0.4})
        features.append({"name": "SmurfPatternDetected", "contribution": 0.3})
        features.append({"name": "AccountActivity", "contribution": 0.2})
    elif score > 0.8:
        features.append({"name": "HighMLScore", "contribution": 0.5})
        features.append({"name": "TransactionFrequency", "contribution": 0.3})
        features.append({"name": "SenderGeography", "contribution": 0.1})
    else:
        features.append({"name": "TransactionAmount", "contribution": round(random.uniform(0.1, 0.6), 2)})
        features.append({"name": "HistoricalAvg", "contribution": round(random.uniform(0.05, 0.3), 2)})

    # Sort by contribution and take top 3
    features_sorted = sorted(features, key=lambda x: x['contribution'], reverse=True)[:3]
    return json.dumps(features_sorted) # Return as JSON string

# Register the Python function as a UDF (User Defined Function)
spark.udf.register("get_shap_features_udf", get_shap_features, StringType())

final_alerts_with_shap = final_alerts.withColumn(
    "shap_features_json",
    col("ml_fraud_score").cast(DoubleType()), # Pass ML score as first arg
    col("amount").cast(DoubleType()), # Pass amount as second arg
    col("is_smurfing_rule").cast(BooleanType()), # Pass smurfing rule as third arg
).withColumn(
    "shap_features_json",
    spark.udf.register("get_shap_features_udf", get_shap_features, StringType())(
        col("ml_fraud_score"), col("amount"), col("is_smurfing_rule")
    )
)


# --- Write Alerts (Currently to Console, later to Cassandra) ---
# For a quick start, we'll print to console.
# In a real system, you'd write to Cassandra, and Neo4j would be updated separately
# to build the graph.

query = final_alerts_with_shap.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .trigger(processingTime="5 seconds") # Process micro-batches every 5 seconds
    .start()

print("Spark Streaming query started. Alerts will be printed to console.")
print("Waiting for stream to terminate...")

# Keep the Spark application running until terminated
query.awaitTermination()
print("Spark Streaming query terminated.")
