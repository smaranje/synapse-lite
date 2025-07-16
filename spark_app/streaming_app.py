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
from neo4j import GraphDatabase, basic_auth
import time # For retry logic

# Temporarily disable ML model and LLM imports for refactor stability
# from model import load_model, preprocess_features, explain_prediction
# import requests

# --- Environment Variables ---
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:29092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')
NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'password')
# LLM_SERVICE_URL = os.environ.get('LLM_SERVICE_URL', 'http://flask-llm-service:5000/generate-sar') # Temporarily unused

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

# --- Load ML Model (Temporarily skipped) ---
ml_model = None # Set to None for now
print("ML Model loading skipped for refactor stability.")
# try:
#     ml_model = load_model("/app/bitcoin_fraud_model.pkl") # Path to dummy model
#     print("ML Model loaded successfully.")
# except Exception as e:
#     print(f"Error loading ML model: {e}. ML predictions will be skipped.", file=sys.stderr)
#     ml_model = None

# --- Define Kafka Schema for Bitcoin Transaction Data ---
# Read 'inputs' and 'out' as StringType to avoid ClassCastException from Kafka source
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

# Define schema for nested 'inputs' and 'out' structures for parsing
input_schema = ArrayType(StructType([
    StructField("prev_out", StructType([
        StructField("addr", StringType()),
        StructField("value", LongType())
    ])),
    StructField("scriptSig", StringType()),
    StructField("sequence", LongType())
]))

output_schema = ArrayType(StructType([
    StructField("value", LongType()),
    StructField("hash", StringType()),
    StructField("script", StringType()),
    StructField("addr", StringType()),
    StructField("spent", BooleanType())
]))

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

# --- Feature Engineering and JSON Parsing within Spark ---
# Calculate fee_per_byte
features_df = parsed_df.withColumn("fee_per_byte", col("fee") / col("size"))

# Parse 'inputs' and 'out' JSON strings into structured columns
features_df = features_df.withColumn("inputs_parsed", from_json(col("inputs"), input_schema)) \
                         .withColumn("out_parsed", from_json(col("out"), output_schema))

# UDF to sum values from parsed input/output arrays
def sum_values_from_parsed_array(arr):
    if arr is None:
        return 0
    total = 0
    for item in arr:
        # For inputs, value is nested under prev_out
        if 'prev_out' in item and 'value' in item['prev_out']:
            try:
                total += float(item['prev_out']['value'])
            except (ValueError, TypeError):
                pass
        # For outputs, value is directly under the item
        elif 'value' in item:
            try:
                total += float(item['value'])
            except (ValueError, TypeError):
                pass
    return total

sum_values_udf = udf(sum_values_from_parsed_array, DoubleType())

features_df = features_df.withColumn("total_input_value", sum_values_udf(col("inputs_parsed"))) \
                         .withColumn("total_output_value", sum_values_udf(col("out_parsed")))

# --- Apply Smurfing Rule as a Spark UDF ---
# The original detect_smurfing_rule flags transfers < 100 USD where either account contains "SMURF".
# We need to extract sender/receiver accounts from parsed inputs/outputs.
# For simplicity, we'll check if ANY input/output address contains "SMURF".
# This UDF will operate on the parsed 'inputs_parsed' and 'out_parsed' columns.

def detect_smurfing_rule_spark(tx_type, amount, inputs_parsed, out_parsed):
    if tx_type != "transfer": # Assuming 'transfer' is a transaction type we'd infer or receive
        return False # This rule is for transfers only

    if amount is not None and float(amount) >= 100:
        return False

    # Check sender accounts (from inputs)
    if inputs_parsed:
        for input_data in inputs_parsed:
            if 'prev_out' in input_data and 'addr' in input_data['prev_out']:
                if "SMURF" in str(input_data['prev_out']['addr']).upper():
                    return True
    
    # Check receiver accounts (from outputs)
    if out_parsed:
        for output_data in out_parsed:
            if 'addr' in output_data:
                if "SMURF" in str(output_data['addr']).upper():
                    return True
    return False

detect_smurfing_udf = udf(detect_smurfing_rule_spark, BooleanType())

# Add a dummy 'transaction_type' for now, or infer it if possible from data
# For now, we'll assume all transactions are "transfer" for the rule to apply.
# In a real scenario, you'd derive this from transaction characteristics.
features_df = features_df.withColumn("transaction_type", lit("transfer"))

features_df = features_df.withColumn(
    "isSmurfingRule",
    detect_smurfing_udf(col("transaction_type"), col("total_output_value"), col("inputs_parsed"), col("out_parsed"))
)

# Add dummy ML prediction columns for now
features_df = features_df.withColumn("mlFraudScore", lit(0.0).cast(DoubleType()))
features_df = features_df.withColumn("mlPrediction", lit(0).cast(IntegerType())) # Use IntegerType for boolean-like prediction
features_df = features_df.withColumn("shap_features_json", lit("{}").cast(StringType()))


# --- Define process_batch function to write to Neo4j directly from Spark DataFrame ---
def process_batch(df, epoch_id):
    if df.isEmpty(): # Correct way to check for empty Spark DataFrame
        print(f"Batch {epoch_id}: No data received.")
        return

    print(f"Processing batch {epoch_id} with {df.count()} records.")
    # df.show(5, truncate=False) # Uncomment for debugging to see batch content

    # --- ML Model and LLM (Currently Mocked/Skipped for Stability) ---
    # In a real scenario, you would apply the ML model here using Spark MLlib,
    # or if using a Python scikit-learn model, you'd use a Pandas UDF.
    # For now, mlFraudScore, mlPrediction, and shap_features_json are dummy values.

    # --- Write to Neo4j using foreachPartition ---
    # This is the most efficient and robust way to write to external systems
    # from Spark executors in a distributed manner.
    def write_partition_to_neo4j(partition_rows):
        # Establish Neo4j connection per partition (or reuse if connection pooling is set up)
        # It's crucial to establish a new driver instance here for each partition
        # to avoid serialization issues of the driver object itself when sent to executors.
        local_neo4j_driver = None
        try:
            local_neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD))
            with local_neo4j_driver.session() as session:
                for row in partition_rows:
                    # Extract data from Spark Row object
                    tx_hash = row["hash"]
                    ml_fraud_score = row["mlFraudScore"]
                    is_smurfing_rule = row["isSmurfingRule"]
                    timestamp = row["time"]
                    vin_sz = row["vin_sz"]
                    vout_sz = row["vout_sz"]
                    size = row["size"]
                    fee = row["fee"]
                    fee_per_byte = row["fee_per_byte"]
                    total_input_value = row["total_input_value"]
                    total_output_value = row["total_output_value"]
                    shap_features_json = row["shap_features_json"]

                    tx_node_props = {
                        "hash": tx_hash,
                        "mlFraudScore": ml_fraud_score,
                        "isSmurfingRule": is_smurfing_rule,
                        "timestamp": timestamp,
                        "vin_sz": vin_sz,
                        "vout_sz": vout_sz,
                        "size": size,
                        "fee": fee,
                        "feePerByte": fee_per_byte,
                        "totalInputValue": total_input_value,
                        "totalOutputValue": total_output_value,
                        "shapFeaturesJson": shap_features_json
                    }

                    # Merge the transaction node
                    session.run("""
                        MERGE (t:Transaction {hash: $hash})
                        SET t += $props
                        """, hash=tx_hash, props=tx_node_props)

                    # Process inputs for Address nodes and relationships
                    # Use the original 'inputs' string column, then parse it within the executor
                    inputs_json_str = row["inputs"]
                    input_addresses_data = []
                    if inputs_json_str:
                        try:
                            input_addresses_data = json.loads(inputs_json_str)
                        except json.JSONDecodeError:
                            # print(f"Warning: Could not decode inputs JSON string for hash {tx_hash}", file=sys.stderr)
                            pass # Suppress verbose warnings in logs for now

                    if input_addresses_data:
                        for input_data in input_addresses_data:
                            if isinstance(input_data, dict) and 'prev_out' in input_data and input_data['prev_out'] and 'addr' in input_data['prev_out']:
                                addr_id = input_data['prev_out']['addr']
                                if addr_id: # Ensure address is not None/empty
                                    session.run("""
                                        MERGE (a:Address {id: $addr_id})
                                        MERGE (a)-[:SENT]->(t:Transaction {hash: $tx_hash})
                                        """, addr_id=addr_id, tx_hash=tx_hash)

                    # Process outputs for Address nodes and relationships
                    # Use the original 'out' string column, then parse it within the executor
                    out_json_str = row["out"]
                    output_addresses_data = []
                    if out_json_str:
                        try:
                            output_addresses_data = json.loads(out_json_str)
                        except json.JSONDecodeError:
                            # print(f"Warning: Could not decode out JSON string for hash {tx_hash}", file=sys.stderr)
                            pass # Suppress verbose warnings in logs for now

                    if output_addresses_data:
                        for output_data in output_addresses_data:
                            if isinstance(output_data, dict) and 'addr' in output_data:
                                addr_id = output_data['addr']
                                if addr_id: # Ensure address is not None/empty
                                    session.run("""
                                        MERGE (a:Address {id: $addr_id})
                                        MERGE (t:Transaction {hash: $tx_hash})-[:SENT_TO]->(a)
                                        """, addr_id=addr_id, tx_hash=tx_hash)
        except Exception as e:
            print(f"Error writing partition to Neo4j: {e}", file=sys.stderr)
        finally:
            if local_neo4j_driver:
                local_neo4j_driver.close() # Close driver for each partition

    # Apply the function to each partition of the DataFrame
    df.foreachPartition(write_partition_to_neo4j)

    print(f"Batch {epoch_id}: Finished processing and attempting to write to Neo4j.")

    # --- Call LLM Service for Alerts (Temporarily skipped) ---
    # This part would need to be re-introduced carefully, potentially by collecting
    # only the fraud-flagged transactions to the driver for LLM calls, or
    # by making the LLM call within a Pandas UDF if we re-introduce Pandas.
    # For now, it's commented out to ensure core stability.
    # fraud_df = df.filter((col("mlPrediction") == 1) | (col("isSmurfingRule") == True))
    # for row in fraud_df.collect(): # This would collect only fraud-flagged rows
    #     print(f"Fraud alert detected for transaction {row['hash']}! Calling LLM service...", file=sys.stderr)
    #     alert_data = {
    #         "transaction_hash": str(row["hash"]),
    #         "ml_fraud_score": float(row["mlFraudScore"]),
    #         "is_smurfing_rule": bool(row["isSmurfingRule"]),
    #         "num_inputs": int(row["vin_sz"]),
    #         "num_outputs": int(row["vout_sz"]),
    #         "total_input_value": float(row["total_input_value"]),
    #         "total_output_value": float(row["total_output_value"]),
    #         "transaction_fee": int(row["fee"]),
    #         "fee_per_byte": float(row["fee_per_byte"]),
    #         "shap_features_json": str(row["shap_features_json"])
    #     }
    #     try:
    #         import requests # Ensure requests is imported if uncommenting this block
    #         response = requests.post(LLM_SERVICE_URL, json=alert_data, timeout=30)
    #         response.raise_for_status()
    #         sar_response = response.json()
    #         print(f"LLM SAR Draft for {row['hash']}:\n{sar_response.get('sar_draft', 'No SAR generated.')}\n", file=sys.stderr)
    #     except requests.exceptions.RequestException as req_err:
    #         print(f"Error calling LLM service for {row['hash']}: {req_err}", file=sys.stderr)
    #     except json.JSONDecodeError as json_err:
    #         print(f"Error decoding JSON response from LLM service for {row['hash']}: {json_err}. Response: {response.text}", file=sys.stderr)
    #     except Exception as e:
    #         print(f"An unexpected error occurred when calling LLM service for {row['hash']}: {e}", file=sys.stderr)


# Start the streaming query
print("Starting Spark streaming query...")
query = features_df \
    .writeStream \
    .outputMode("append") \
    .foreachBatch(process_batch) \
    .trigger(processingTime="10 seconds") \
    .start()

print("Spark streaming query terminated. Awaiting termination...")
query.awaitTermination()
