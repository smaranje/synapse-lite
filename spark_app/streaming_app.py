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
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0")
    .config("spark.jars",
            "/opt/bitnami/spark/jars/"
            "neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar")
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
        break
    except Exception:
        time.sleep(5)

if neo4j_driver is None:
    print("‼ Could not connect to Neo4j – exiting.", file=sys.stderr)
    sys.exit(1)

# ----------------------------------------------------------------------------
# 4. Load dummy ML model
# ----------------------------------------------------------------------------

ml_model = load_dummy_model()

# ----------------------------------------------------------------------------
# 5. Kafka schema & stream
# ----------------------------------------------------------------------------

schema = (
    StructType()
    .add("hash", StringType())
    .add("time", LongType())
    .add("vin_sz", LongType())
    .add("vout_sz", LongType())
    .add("size", LongType())
    .add("fee", LongType())
    .add("inputs", ArrayType(MapType(StringType(), StringType())))
    .add("out", ArrayType(MapType(StringType(), StringType())))
)

kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BROKER)
    .option("subscribe", KAFKA_TOPIC)
    .option("startingOffsets", "latest")
    .load()
)

parsed_df = (
    kafka_df
    .selectExpr("CAST(value AS STRING) AS json_value")
    .select(from_json(col("json_value"), schema).alias("data"))
    .select("data.*")
)

# ----------------------------------------------------------------------------
# 6. Feature engineering
# ----------------------------------------------------------------------------

def sum_values(arr: List[Dict[str, Any]]) -> float:
    total = 0.0
    for item in arr or []:
        try:
            total += float(item.get("value", 0))
        except Exception:
            pass
    return total

sum_values_udf = udf(sum_values, DoubleType())

features_df = (
    parsed_df
    .withColumn("total_input_value", sum_values_udf(col("inputs")))
    .withColumn("total_output_value", sum_values_udf(col("out")))
    .withColumn("fee_per_byte", col("fee") / col("size"))
)

# ----------------------------------------------------------------------------
# 7. Batch processing
# ----------------------------------------------------------------------------

def process_batch(df, epoch_id):
    # collect to pandas first to avoid Spark partition serialization issues
    pdf = df.toPandas()
    if pdf.empty:
        print(f"• Batch {epoch_id}: no records.")
        return

    count = len(pdf)
    print(f"• Batch {epoch_id}: {count} records.")

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
                "timestamp":       int(row["time"]),
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
                "MERGE (t:Transaction {hash:$hash}) SET t += $props",
                **props
            )

# ----------------------------------------------------------------------------
# 8. Start streaming query
# ----------------------------------------------------------------------------

query = (
    features_df.writeStream
    .outputMode("append")
    .foreachBatch(process_batch)
    .trigger(processingTime="10 seconds")
    .start()
)

query.awaitTermination()
