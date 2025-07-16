# spark_app/streaming_app.py
import os
import sys
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, lit, struct, to_json, udf
from pyspark.sql.types import StructType, StringType, LongType, DoubleType, BooleanType, ArrayType, MapType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.linalg import Vectors
from neo4j import GraphDatabase, basic_auth
import time # For retry logic
from model import load_model, preprocess_features, explain_prediction
from fraud_rules import detect_smurfing_rule # Corrected function name

import pandas as pd # Needed for toPandas and apply
import requests # Import requests here as it's used in process_batch for LLM call

# --- Environment Variables ---
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:29092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')
NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'password')
LLM_SERVICE_URL = os.environ.get('LLM_SERVICE_URL', 'http://flask-llm-service:5000/generate-sar')

# --- Spark Session Initialization ---
print("Initializing Spark Session...")
spark = SparkSession.builder \
    .appName("BitcoinFraudDetection") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.jars", "/app/neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar") \
    .config("spark.driver.extraJavaOptions", "-Dlog4j.configuration=file:/opt/bitnami/spark/conf/log4j2.properties") \
    .config("spark.executor.extraJavaOptions", "-Dlog4j.configuration=file:/opt/bitnami/spark/conf/log4j2.properties") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN") # Reduce verbosity of Spark logs
print("Spark Session initialized.")

# --- Neo4j Driver Initialization with Retry ---
neo4j_driver = None
print(f"Attempting to connect to Neo4j at {NEO4J_URI}...")
for i in range(10): # Retry 10 times
    try:
        neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD))
        neo4j_driver.verify_connectivity() # Verify connection immediately
        print("Neo4j driver initialized and connected successfully.")
        break
    except Exception as e:
        print(f"Neo4j connection attempt {i+1}/10 failed: {e}. Retrying in 10 seconds...", file=sys.stderr)
        time.sleep(10)
if not neo4j_driver:
    print("Failed to connect to Neo4j after multiple retries. Exiting Spark application.", file=sys.stderr)
    sys.exit(1)

# --- Load ML Model ---
try:
    ml_model = load_model("/app/bitcoin_fraud_model.pkl") # Path to dummy model
    print("ML Model loaded successfully.")
except Exception as e:
    print(f"Error loading ML model: {e}. ML predictions will be skipped.", file=sys.stderr)
    ml_model = None

# --- Define Kafka Schema for Bitcoin Transaction Data ---
# Read 'inputs' and 'out' as StringType to avoid ClassCastException
schema = StructType() \
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
    .load()

# Parse the Kafka value (JSON string) into a structured DataFrame
parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json_value") \
    .select(from_json(col("json_value"), schema).alias("data")) \
    .select("data.*")

# --- Feature Engineering ---
# Calculate fee_per_byte
features_df = parsed_df.withColumn("fee_per_byte", col("fee") / col("size"))

# UDF to sum values from nested arrays (inputs/outputs) - now expects JSON string
def sum_values_from_json_string(json_str):
    if json_str is None:
        return 0
    try:
        arr = json.loads(json_str)
        if not isinstance(arr, list): # Ensure it's a list after parsing
            return 0
        total = 0
        for item in arr:
            if isinstance(item, dict) and 'value' in item:
                try:
                    total += float(item['value'])
                except (ValueError, TypeError):
                    pass # Ignore non-numeric values
        return total
    except json.JSONDecodeError:
        return 0 # Handle invalid JSON strings

sum_values_udf = udf(sum_values_from_json_string, DoubleType())

# Apply UDF to the 'inputs' and 'out' columns (which are now StringType)
features_df = features_df.withColumn("total_input_value", sum_values_udf(col("inputs"))) \
                         .withColumn("total_output_value", sum_values_udf(col("out")))


# --- Apply ML Model and Fraud Rules ---
def process_batch(df, epoch_id):
    # CRITICAL FIX: Repartition the DataFrame before converting to Pandas
    # This can help break problematic internal serialization states
    # Use repartition(1) to collect all data to a single partition for toPandas,
    # which is generally safer for small to medium batches in streaming.
    repartitioned_df = df.repartition(1) # <--- ADDED THIS LINE

    # Convert Spark DataFrame to Pandas DataFrame
    # All columns passed to toPandas should now be simple types (string, long, double, boolean)
    pandas_df = repartitioned_df.toPandas() # <--- CHANGED TO USE repartitioned_df

    if pandas_df.empty:
        print(f"Batch {epoch_id}: No data received or all data filtered out after conversion.")
        return

    print(f"Processing batch {epoch_id} with {len(pandas_df)} records.")

    if ml_model and not pandas_df.empty:
        processed_df, feature_names = preprocess_features(pandas_df)

        predictions = ml_model.predict(processed_df)
        probabilities = ml_model.predict_proba(processed_df) # Get probabilities for SHAP

        # Explain predictions using SHAP
        shap_values = explain_prediction(ml_model, processed_df, feature_names)

        # Add predictions and SHAP values back to DataFrame
        pandas_df['mlFraudScore'] = [prob[1] for prob in probabilities] # Probability of fraud class
        pandas_df['mlPrediction'] = predictions
        
        # Ensure shap_features is a JSON string
        pandas_df['shap_features_json'] = [
            json.dumps({name: value for name, value in zip(feature_names, shap_val) if abs(value) > 0.01})
            for shap_val in shap_values
        ]
    else:
        pandas_df['mlFraudScore'] = 0.0 # Default if no model
        pandas_df['mlPrediction'] = 0 # Default if no model
        pandas_df['shap_features_json'] = "{}" # Default to empty JSON object

    # Apply smurfing rule
    pandas_df['isSmurfingRule'] = pandas_df.apply(detect_smurfing_rule, axis=1)

    # --- Write to Neo4j ---
    # Prepare data for Neo4j write in a format that SET t += $props can use
    records_to_neo4j = []
    for index, row in pandas_df.iterrows():
        # Ensure all values are cast to appropriate types for Neo4j
        tx_node_props = {
            "hash": str(row["hash"]),
            "mlFraudScore": float(row["mlFraudScore"]),
            "isSmurfingRule": bool(row["isSmurfingRule"]),
            "timestamp": int(row["time"]), # Use the original 'time' from Kafka, which is epoch milliseconds
            "vin_sz": int(row["vin_sz"]),
            "vout_sz": int(row["vout_sz"]),
            "size": int(row["size"]),
            "fee": int(row["fee"]),
            "feePerByte": float(row["fee_per_byte"]),
            "totalInputValue": float(row["total_input_value"]),
            "totalOutputValue": float(row["total_output_value"]),
            "shapFeaturesJson": str(row["shap_features_json"]) # Ensure it's a string
        }
        records_to_neo4j.append(tx_node_props)

        # Parse inputs and outputs from JSON strings (which are now directly from Kafka as StringType)
        input_addresses_data = []
        if pd.notna(row["inputs"]): # 'inputs' column is now a string
            try:
                input_addresses_data = json.loads(row["inputs"])
            except json.JSONDecodeError:
                print(f"Warning: Could not decode inputs JSON string for hash {row['hash']}", file=sys.stderr)

        output_addresses_data = []
        if pd.notna(row["out"]): # 'out' column is now a string
            try:
                output_addresses_data = json.loads(row["out"])
            except json.JSONDecodeError:
                print(f"Warning: Could not decode out JSON string for hash {row['hash']}", file=sys.stderr)


        # Use a single write transaction for efficiency per batch
        try:
            with neo4j_driver.session() as session:
                # Merge the transaction node
                session.run("""
                    MERGE (t:Transaction {hash: $hash})
                    SET t += $props
                    """, hash=tx_node_props["hash"], props=tx_node_props) # Use tx_node_props here

                # Create/Update Address nodes and relationships for inputs
                for input_data in input_addresses_data:
                    if isinstance(input_data, dict) and 'prev_out' in input_data and isinstance(input_data['prev_out'], dict) and 'addr' in input_data['prev_out']:
                        addr_id = input_data['prev_out']['addr']
                        session.run("""
                            MERGE (a:Address {id: $addr_id})
                            MERGE (a)-[:SENT]->(t:Transaction {hash: $tx_hash})
                            """, addr_id=addr_id, tx_hash=tx_node_props["hash"])
                
                # Create/Update Address nodes and relationships for outputs
                for output_data in output_addresses_data:
                    if isinstance(output_data, dict) and 'addr' in output_data:
                        addr_id = output_data['addr']
                        session.run("""
                            MERGE (a:Address {id: $addr_id})
                            MERGE (t:Transaction {hash: $tx_hash})-[:SENT_TO]->(a)
                            """, addr_id=addr_id, tx_hash=tx_node_props["hash"])

        except Exception as e:
            print(f"Batch {epoch_id}: Error writing transaction {row['hash']} to Neo4j: {e}", file=sys.stderr)


    # Final confirmation of batch write
    print(f"Batch {epoch_id}: Attempted to write {len(records_to_neo4j)} records to Neo4j.")


    # --- Call LLM Service for Alerts ---
    for index, row in pandas_df.iterrows():
        # Only call LLM if fraud detected or rule triggered
        if row["mlPrediction"] == 1 or row["isSmurfingRule"]:
            print(f"Fraud alert detected for transaction {row['hash']}! Calling LLM service...", file=sys.stderr)
            alert_data = {
                "transaction_hash": str(row["hash"]),
                "ml_fraud_score": float(row["mlFraudScore"]),
                "is_smurfing_rule": bool(row["isSmurfingRule"]),
                "num_inputs": int(row["vin_sz"]),
                "num_outputs": int(row["vout_sz"]),
                "total_input_value": float(row["total_input_value"]),
                "total_output_value": float(row["total_output_value"]),
                "transaction_fee": int(row["fee"]),
                "fee_per_byte": float(row["fee_per_byte"]),
                "shap_features_json": str(row["shap_features_json"])
            }
            try:
                response = requests.post(LLM_SERVICE_URL, json=alert_data, timeout=30)
                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                sar_response = response.json()
                print(f"LLM SAR Draft for {row['hash']}:\n{sar_response.get('sar_draft', 'No SAR generated.')}\n", file=sys.stderr)
            except requests.exceptions.RequestException as req_err:
                print(f"Error calling LLM service for {row['hash']}: {req_err}", file=sys.stderr)
            except json.JSONDecodeError as json_err:
                print(f"Error decoding JSON response from LLM service for {row['hash']}: {json_err}. Response: {response.text}", file=sys.stderr)
            except Exception as e:
                print(f"An unexpected error occurred when calling LLM service for {row['hash']}: {e}", file=sys.stderr)


# Start the streaming query
print("Starting Spark streaming query...")
query = features_df \
    .writeStream \
    .outputMode("append") \
    .foreachBatch(process_batch) \
    .trigger(processingTime="10 seconds") \
    .start()

print("Spark streaming query terminated.")
query.awaitTermination()