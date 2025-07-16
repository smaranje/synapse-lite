# spark_app/streaming_app.py
import os
import sys
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, lit, udf, explode, when
from pyspark.sql.types import (
    StructType, StringType, LongType, DoubleType, BooleanType, ArrayType, MapType,
    StructField, IntegerType
)
# REMOVED Neo4j, ML, LLM imports for this test
# from neo4j import GraphDatabase, basic_auth
# import time
# from model import load_model, preprocess_features, explain_prediction
# import requests

# --- Environment Variables ---
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:29092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')
# REMOVED Neo4j and LLM service URLs as they are not used in this minimal test
# NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
# NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
# NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'password')
# LLM_SERVICE_URL = os.environ.get('LLM_SERVICE_URL', 'http://flask-llm-service:5000/generate-sar')

# --- Spark Session Initialization ---
print("Initializing Spark Session...")
spark = SparkSession.builder \
    .appName("BitcoinFraudDetectionMinimal") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.6") \
    .config("spark.driver.extraJavaOptions", "-Dlog4j.configuration=file:/opt/bitnami/spark/conf/log4j2.properties") \
    .config("spark.executor.extraJavaOptions", "-Dlog4j.configuration=file:/opt/bitnami/spark/conf/log4j2.properties") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN") # Reduce verbosity of Spark logs
print("Spark Session initialized.")

# --- Neo4j Driver Initialization (REMOVED for this test) ---
# ml_model = None # Set to None for now
print("Neo4j driver initialization skipped for this test.")
print("ML Model loading skipped for this test.")


# --- Define Kafka Schema for RAW Kafka Value ---
# ONLY read the 'value' column as a string.
# This avoids Spark trying to infer or deserialize complex structures directly from Kafka.
# The `key`, `topic`, etc., are standard Kafka metadata columns.
kafka_raw_schema = StructType() \
    .add("key", StringType()) \
    .add("value", StringType()) \
    .add("topic", StringType()) \
    .add("partition", IntegerType()) \
    .add("offset", LongType()) \
    .add("timestamp", LongType()) \
    .add("timestampType", IntegerType())

# --- Define the actual Bitcoin Transaction Schema for later parsing ---
# This schema is used *after* reading the raw Kafka string value.
bitcoin_tx_schema = StructType() \
    .add("hash", StringType()) \
    .add("ver", LongType()) \
    .add("vin_sz", LongType()) \
    .add("vout_sz", LongType()) \
    .add("size", LongType()) \
    .add("weight", LongType()) \
    .add("fee", LongType()) \
    .add("relayed_by", StringType()) \
    .add("lock_time", LongType()) \
    .add("tx_index", LongType()) \
    .add("double_spend", BooleanType()) \
    .add("time", LongType()) \
    .add("block_height", LongType()) \
    .add("inputs", StringType()) \
    .add("out", StringType())


# --- Read Data from Kafka ---
print(f"Reading from Kafka topic '{KAFKA_TOPIC}' on broker '{KAFKA_BROKER}'...")
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load() \
    .selectExpr("CAST(value AS STRING) as json_value") # Cast value to string immediately


# --- Apply Bitcoin Transaction Schema AFTER initial Kafka read ---
# This ensures Spark handles the raw string first, then parses the JSON.
processed_df = kafka_df.select(from_json(col("json_value"), bitcoin_tx_schema).alias("data")) \
                       .select("data.*")

# --- Define process_batch function for console sink ---
def process_batch(df, epoch_id):
    # No df.isEmpty() or df.count() calls here to avoid immediate actions
    # If the batch is truly empty, foreachPartition will simply not execute its inner logic.
    
    # Collect data in partitions and print to console
    def print_partition_to_console(partition_rows):
        rows_in_partition = 0
        for row in partition_rows:
            rows_in_partition += 1
            # Print a simplified representation of the row
            # Safely get values, as some might be null if parsing failed or data is malformed
            tx_hash = row['hash'] if 'hash' in row and row['hash'] is not None else 'N/A'
            tx_time = row['time'] if 'time' in row and row['time'] is not None else 'N/A'
            vin_sz = row['vin_sz'] if 'vin_sz' in row and row['vin_sz'] is not None else 'N/A'
            vout_sz = row['vout_sz'] if 'vout_sz' in row and row['vout_sz'] is not None else 'N/A'
            
            print(f"Batch {epoch_id}, Partition Row: Hash={tx_hash}, Time={tx_time}, InputsSize={vin_sz}, OutputsSize={vout_sz}")
        if rows_in_partition > 0:
            print(f"Batch {epoch_id}: Partition processed {rows_in_partition} records.")
        else:
            print(f"Batch {epoch_id}: Partition received 0 records.")


    df.foreachPartition(print_partition_to_console)
    print(f"Batch {epoch_id}: Finished processing (console output).")


# Start the streaming query
print("Starting Spark streaming query...")
query = processed_df \
    .writeStream \
    .outputMode("append") \
    .foreachBatch(process_batch) \
    .trigger(processingTime="10 seconds") \
    .start()

print("Spark streaming query terminated. Awaiting termination...")
query.awaitTermination()