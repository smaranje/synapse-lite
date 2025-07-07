# spark_app/streaming_app.py
#
# End-to-end Spark Structured-Streaming job for Synapse-Lite:
#   • Consumes Bitcoin-style transactions from Kafka
#   • Engineers features, scores a Random-Forest model, applies “smurfing” rule
#   • Writes full Transaction+Address graph to Neo4j with all properties set
#   • Sends high-risk alerts to the LLM micro-service for SAR drafting
#
# ---------------------------------------------------------------------------

import os
import sys
import json
import time
from typing import Any, Dict, List

import pandas as pd
from neo4j import GraphDatabase, basic_auth
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import (
    StructType, StringType, LongType, DoubleType, BooleanType,
    ArrayType, MapType
)
from pyspark.ml.linalg import Vectors   # noqa: F401  (imported for model utils)

# Project-local helpers
from model import load_model, preprocess_features, explain_prediction
from fraud_rules import apply_smurfing_rule

# ---------------------------------------------------------------------------
# 1. Environment
# ---------------------------------------------------------------------------

KAFKA_BROKER     = os.environ.get("KAFKA_BROKER",  "kafka:29092")
KAFKA_TOPIC      = os.environ.get("KAFKA_TOPIC",   "transactions")
NEO4J_URI        = os.environ.get("NEO4J_URI",     "bolt://neo4j:7687")
NEO4J_USERNAME   = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD   = os.environ.get("NEO4J_PASSWORD", "password")
LLM_SERVICE_URL  = os.environ.get("LLM_SERVICE_URL",
                                  "http://flask-llm-service:5000/generate-sar")

# ---------------------------------------------------------------------------
# 2. Spark session
# ---------------------------------------------------------------------------

print("⇢ Initialising Spark …")
spark = (
    SparkSession.builder
    .appName("BitcoinFraudDetection")
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0")
    .config("spark.jars",
            "/opt/bitnami/spark/jars/"
            "neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar")
    .config("spark.driver.extraJavaOptions",
            "-Dlog4j.configuration=file:/opt/bitnami/spark/conf/log4j2.properties")
    .config("spark.executor.extraJavaOptions",
            "-Dlog4j.configuration=file:/opt/bitnami/spark/conf/log4j2.properties")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")
print("✓ Spark session ready.")

# ---------------------------------------------------------------------------
# 3. Neo4j driver (with retry)
# ---------------------------------------------------------------------------

print(f"⇢ Connecting to Neo4j at {NEO4J_URI} …")
neo4j_driver = None
for attempt in range(1, 11):
    try:
        neo4j_driver = GraphDatabase.driver(
            NEO4J_URI, auth=basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        neo4j_driver.verify_connectivity()
        print("✓ Neo4j connection established.")
        break
    except Exception as exc:
        print(f"✗ Attempt {attempt}/10 failed: {exc}", file=sys.stderr)
        time.sleep(10)

if neo4j_driver is None:
    print("‼ Could not connect to Neo4j – exiting.", file=sys.stderr)
    sys.exit(1)

# ---------------------------------------------------------------------------
# 4. Load (dummy) ML model
# ---------------------------------------------------------------------------

try:
    ml_model = load_model("/app/bitcoin_fraud_model.pkl")
    print("✓ ML model loaded.")
except Exception as exc:
    print(f"⚠ ML model load failed – scoring disabled: {exc}", file=sys.stderr)
    ml_model = None

# ---------------------------------------------------------------------------
# 5. Kafka schema & stream
# ---------------------------------------------------------------------------

schema = (
    StructType()
    .add("hash",          StringType())
    .add("ver",           LongType())
    .add("vin_sz",        LongType())
    .add("vout_sz",       LongType())
    .add("size",          LongType())
    .add("weight",        LongType())
    .add("fee",           LongType())
    .add("relayed_by",    StringType())
    .add("lock_time",     LongType())
    .add("tx_index",      LongType())
    .add("double_spend",  BooleanType())
    .add("time",          LongType())
    .add("block_height",  LongType())
    .add("inputs",        ArrayType(MapType(StringType(), StringType())))
    .add("out",           ArrayType(MapType(StringType(), StringType())))
)

print(f"⇢ Subscribing to Kafka topic '{KAFKA_TOPIC}' …")
kafka_df = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", KAFKA_BROKER)
    .option("subscribe", KAFKA_TOPIC)
    .option("startingOffsets", "latest")
    .load()
)

parsed_df = (
    kafka_df.selectExpr("CAST(value AS STRING) AS json_value")
    .select(from_json(col("json_value"), schema).alias("data"))
    .select("data.*")
)

# ---------------------------------------------------------------------------
# 6. Feature engineering
# ---------------------------------------------------------------------------

features_df = parsed_df.withColumn("fee_per_byte", col("fee") / col("size"))

def sum_values(arr: List[Dict[str, Any]]) -> float:
    if not arr:
        return 0.0
    total = 0.0
    for item in arr:
        try:
            total += float(item.get("value", 0))
        except (ValueError, TypeError):
            pass
    return total

sum_values_udf = udf(sum_values, DoubleType())

features_df = (
    features_df
    .withColumn("total_input_value",  sum_values_udf(col("inputs")))
    .withColumn("total_output_value", sum_values_udf(col("out")))
)

# ---------------------------------------------------------------------------
# 7. Per-batch processing
# ---------------------------------------------------------------------------

def process_batch(df, epoch_id):
    if df.isEmpty():
        print(f"• Batch {epoch_id}: no records.")
        return

    print(f"• Batch {epoch_id}: {df.count()} records.")

    pdf = df.toPandas()

    # --- ML scoring --------------------------------------------------------
    if ml_model is not None and not pdf.empty:
        X, feat_names = preprocess_features(pdf)
        pdf["mlPrediction"] = ml_model.predict(X)
        pdf["mlFraudScore"] = [p[1] for p in ml_model.predict_proba(X)]
        shap_vals = explain_prediction(ml_model, X, feat_names)
        pdf["shap_features_json"] = [
            json.dumps({
                n: v for n, v in zip(feat_names, shap_row) if abs(v) > 0.01
            })
            for shap_row in shap_vals
        ]
    else:
        pdf["mlPrediction"]      = 0
        pdf["mlFraudScore"]      = 0.0
        pdf["shap_features_json"]= "{}"

    # --- Rule engine -------------------------------------------------------
    pdf["isSmurfingRule"] = pdf.apply(apply_smurfing_rule, axis=1)

    # --- Neo4j write -------------------------------------------------------
    try:
        with neo4j_driver.session() as session:
            for _, row in pdf.iterrows():
                props = {
                    "hash":             str(row["hash"]),
                    "mlFraudScore":     float(row["mlFraudScore"]),
                    "isSmurfingRule":   bool(row["isSmurfingRule"]),
                    "timestamp":        int(row["time"]),
                    "vin_sz":           int(row["vin_sz"]),
                    "vout_sz":          int(row["vout_sz"]),
                    "size":             int(row["size"]),
                    "fee":              int(row["fee"]),
                    "feePerByte":       float(row["fee_per_byte"]),
                    "totalInputValue":  float(row["total_input_value"]),
                    "totalOutputValue": float(row["total_output_value"]),
                    "shapFeaturesJson": str(row["shap_features_json"]),
                }

                # Transaction node
                session.run(
                    """
                    MERGE (t:Transaction {hash:$hash})
                    SET   t += $props
                    """,
                    **props
                )

                # Input addresses
                for inp in (row.get("inputs") or []):
                    addr = inp.get("prev_out", {}).get("addr")
                    if addr:
                        session.run(
                            """
                            MERGE (a:Address {id:$addr})
                            MERGE (a)-[:SENT]->(t:Transaction {hash:$tx})
                            """,
                            addr=addr, tx=props["hash"]
                        )

                # Output addresses
                for outp in (row.get("out") or []):
                    addr = outp.get("addr")
                    if addr:
                        session.run(
                            """
                            MERGE (a:Address {id:$addr})
                            MERGE (t:Transaction {hash:$tx})-[:SENT_TO]->(a)
                            """,
                            addr=addr, tx=props["hash"]
                        )
        print(f"  ↳ Neo4j: wrote {len(pdf)} transactions.")
    except Exception as exc:
        print(f"‼ Neo4j write failed: {exc}", file=sys.stderr)

    # --- LLM alerts --------------------------------------------------------
    import requests  # local import to avoid module-only containers
    for _, row in pdf.iterrows():
        if row["mlPrediction"] == 1 or row["isSmurfingRule"]:
            payload = {
                "transaction_hash":  row["hash"],
                "ml_fraud_score":    row["mlFraudScore"],
                "is_smurfing_rule":  row["isSmurfingRule"],
                "num_inputs":        int(row["vin_sz"]),
                "num_outputs":       int(row["vout_sz"]),
                "total_input_value": float(row["total_input_value"]),
                "total_output_value":float(row["total_output_value"]),
                "transaction_fee":   int(row["fee"]),
                "fee_per_byte":      float(row["fee_per_byte"]),
                "shap_features_json":row["shap_features_json"],
            }
            try:
                r = requests.post(LLM_SERVICE_URL, json=payload, timeout=30)
                r.raise_for_status()
                print(f"  ↳ LLM SAR draft generated for {row['hash']}")
            except Exception as exc:
                print(f"⚠ LLM call failed for {row['hash']}: {exc}",
                      file=sys.stderr)

# ---------------------------------------------------------------------------
# 8. Start streaming query
# ---------------------------------------------------------------------------

print("⇢ Starting Structured-Streaming query …")
query = (
    features_df.writeStream
    .outputMode("append")
    .foreachBatch(process_batch)
    .trigger(processingTime="10 seconds")
    .start()
)

print("✓ Streaming started. Awaiting termination …")
query.awaitTermination()
