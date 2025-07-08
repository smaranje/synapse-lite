# spark_app/streaming_app.py
#
# End-to-end Spark Structured-Streaming job for Synapse-Lite:
#   • Consumes Bitcoin-style transactions from Kafka
#   • Engineers features, scores a dummy ML model, applies rules
#   • Writes graph to Neo4j and sends alerts to LLM micro-service
#

import os
import sys
import json
import time
from typing import Any, Dict, List

from neo4j import GraphDatabase, basic_auth
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import (
    StructType, StringType, LongType, DoubleType, BooleanType,
    ArrayType, MapType
)

# Project-local helpers
from model import predict_fraud_score, get_shap_explanation, load_dummy_model
from fraud_rules import detect_smurfing_rule, detect_high_value_transfer

# ----------------------------------------------------------------------------
# 1. Environment
# ----------------------------------------------------------------------------

KAFKA_BROKER    = os.environ.get("KAFKA_BROKER", "kafka:29092")
KAFKA_TOPIC     = os.environ.get("KAFKA_TOPIC", "transactions")
NEO4J_URI       = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USERNAME  = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD  = os.environ.get("NEO4J_PASSWORD", "password")
LLM_SERVICE_URL = os.environ.get(
    "LLM_SERVICE_URL",
    "http://flask-llm-service:5000/generate-sar"
)

# ----------------------------------------------------------------------------
# 2. Spark session
# ----------------------------------------------------------------------------

spark = (
    SparkSession.builder
    .appName("BitcoinFraudDetection")
    # FIX: Updated Kafka connector version to 3.5.0 (Scala 2.13)
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0")
    .config("spark.jars",
            "/opt/bitnami/spark/jars/"
            "neo4j-connector-apache-spark_2.13-5.3.8_for_spark_3.jar") # Neo4j connector also uses _2.13
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")

# ----------------------------------------------------------------------------
# 3. Neo4j driver (retry)
# ----------------------------------------------------------------------------

neo4j_driver = None
for attempt in range(10):
    try:
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        driver.verify_connectivity()
        neo4j_driver = driver
        print(f"Spark: Successfully connected to Neo4j at {NEO4J_URI}")
        break
    except Exception as e:
        print(f"Spark: Neo4j connection attempt {attempt+1}/10 failed: {e}. Retrying in 5 seconds...", file=sys.stderr)
        time.sleep(5)

if neo4j_driver is None:
    print("Spark: ‼ Could not connect to Neo4j – exiting.", file=sys.stderr)
    sys.exit(1)

# ----------------------------------------------------------------------------
# 4. Load dummy ML model
# ----------------------------------------------------------------------------

ml_model = load_dummy_model()
print("Spark: Dummy ML model loaded.")

# ----------------------------------------------------------------------------
# 5. Kafka schema & stream
# ----------------------------------------------------------------------------

# Define the schema for incoming Kafka messages (Bitcoin transaction data)
schema = (
    StructType()
    .add("hash", StringType())
    .add("time", LongType()) # Timestamp in milliseconds
    .add("vin_sz", LongType()) # Number of inputs
    .add("vout_sz", LongType()) # Number of outputs
    .add("size", LongType()) # Transaction size in bytes
    .add("fee", LongType()) # Transaction fee in satoshis
    # Inputs and outputs are complex structures, define them as Array of Maps
    .add("vin", ArrayType(MapType(StringType(), StringType())))
    .add("vout", ArrayType(MapType(StringType(), StringType())))
    .add("total_input_value", DoubleType())
    .add("total_output_value", DoubleType())
    .add("transaction_fee", DoubleType())
    .add("fee_per_byte", DoubleType())
    # Add optional fields that might be present in the raw data but not strictly used
    .add("locktime", LongType(), True)
    .add("ver", LongType(), True)
    .add("relayed_by", StringType(), True)
    .add("block_height", LongType(), True)
    .add("double_spend", BooleanType(), True)
    .add("rbf", BooleanType(), True)
)


kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BROKER)
    .option("subscribe", KAFKA_TOPIC)
    # Reverting to "latest" as the ClassCastException was the primary issue
    .option("startingOffsets", "latest")
    .option("failOnDataLoss", "false")
    .load()
)

# Parse the JSON value from Kafka messages
parsed_df = (
    kafka_df
    .selectExpr("CAST(value AS STRING) AS json_value")
    .select(from_json(col("json_value"), schema).alias("data"))
    .select("data.*")
)
print("Spark: Kafka stream initialized and schema defined.")

# ----------------------------------------------------------------------------
# 6. Feature engineering (adjusted to use correct column names)
# ----------------------------------------------------------------------------

def sum_values(arr: List[Dict[str, Any]]) -> float:
    total = 0.0
    for item in arr or []:
        try:
            total += float(item.get("value", 0))
        except Exception:
            pass
    return total

# UDF to sum values from input/output arrays
sum_values_udf = udf(sum_values, DoubleType())

# Feature engineering on the parsed DataFrame
features_df = (
    parsed_df
    .withColumnRenamed("time", "timestamp") # Rename 'time' to 'timestamp' for consistency with Neo4j
)
print("Spark: Feature engineering applied.")

# ----------------------------------------------------------------------------
# 7. Batch processing (Neo4j write logic fixed)
# ----------------------------------------------------------------------------

def process_batch(df, epoch_id):
    # Convert Spark DataFrame to Pandas DataFrame for easier Python processing
    pdf = df.toPandas()
    if pdf.empty:
        print(f"Spark: Batch {epoch_id}: no records to process.")
        return

    count = len(pdf)
    print(f"Spark: Batch {epoch_id}: processing {count} records.")

    # ML scoring
    pdf["mlFraudScore"] = pdf.apply(
        lambda row: predict_fraud_score(row.to_dict()), axis=1
    )
    pdf["shap_features_json"] = pdf["mlFraudScore"].apply(
        lambda score: json.dumps(get_shap_explanation({}, score))
    )

    # Rule engine
    pdf["isSmurfingRule"] = pdf.apply(detect_smurfing_rule, axis=1)
    pdf["isHighValue"]    = pdf.apply(detect_high_value_transfer, axis=1)

    # Write to Neo4j
    with neo4j_driver.session() as session:
        for _, row in pdf.iterrows():
            props = {
                "hash":            str(row["hash"]),
                "mlFraudScore":    float(row["mlFraudScore"]),
                "isSmurfingRule":  bool(row["isSmurfingRule"]),
                "isHighValue":     bool(row["isHighValue"]),
                "timestamp":       int(row["timestamp"]),
                "vin_sz":          int(row["vin_sz"]),
                "vout_sz":         int(row["vout_sz"]),
                "size":            int(row["size"]),
                "fee":             int(row["fee"]),
                "feePerByte":      float(row["fee_per_byte"]),
                "totalInputValue": float(row["total_input_value"]),
                "totalOutputValue":float(row["total_output_value"]),
                "shapFeaturesJson":str(row["shap_features_json"]),
            }

            session.run(
                "MERGE (t:Transaction {hash: $hash}) SET t += $props",
                hash=props["hash"],
                props=props
            )

            # Extract addresses and create relationships
            for input_obj in row["vin"]:
                sender_addr = input_obj.get("prev_out", {}).get("addr")
                if sender_addr:
                    session.run(
                        "MERGE (a:Address {id: $address_id})",
                        address_id=sender_addr
                    )
                    session.run(
                        """
                        MATCH (a:Address {id: $address_id})
                        MATCH (t:Transaction {hash: $tx_hash})
                        MERGE (a)-[:SENT]->(t)
                        """,
                        address_id=sender_addr,
                        tx_hash=props["hash"]
                    )

            for output_obj in row["vout"]:
                receiver_addrs = output_obj.get("scriptPubKey", {}).get("addresses")
                if receiver_addrs:
                    for receiver_addr in receiver_addrs:
                        session.run(
                            "MERGE (a:Address {id: $address_id})",
                            address_id=receiver_addr
                        )
                        session.run(
                            """
                            MATCH (t:Transaction {hash: $tx_hash})
                            MATCH (a:Address {id: $address_id})
                            MERGE (t)-[:SENT_TO]->(a)
                            """,
                            address_id=receiver_addr,
                            tx_hash=props["hash"]
                        )
    print(f"Spark: Batch {epoch_id}: {count} records written to Neo4j.")

# ----------------------------------------------------------------------------
# 8. Start streaming query
# ----------------------------------------------------------------------------

query = (
    features_df.writeStream
    .outputMode("append")
    .foreachBatch(process_batch)
    .trigger(processingTime="10 seconds")
    .option("checkpointLocation", "/tmp/spark-checkpoint")
    .start()
)
print("Spark: Streaming query started.")

query.awaitTermination()