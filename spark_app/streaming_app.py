# spark_app/streaming_app.py - Gemini-Only Fraud Analysis
import os
import sys
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, lit, udf
from pyspark.sql.types import (
    StructType, StringType, LongType, DoubleType, BooleanType, ArrayType, StructField
)
from neo4j import GraphDatabase, basic_auth
import time # For retry logic
import requests # Used for LLM service call

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
    .appName("BitcoinFraudDetection_GeminiOnly") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.6") \
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

# --- Define Kafka Schema for Bitcoin Transaction Data ---
# Read 'inputs' and 'out' as StringType from Kafka, then parse them later
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
input_array_schema = ArrayType(StructType([
    StructField("prev_out", StructType([
        StructField("addr", StringType()),
        StructField("value", LongType())
    ])),
    StructField("scriptSig", StringType()),
    StructField("sequence", LongType())
]))

output_array_schema = ArrayType(StructType([
    StructField("value", LongType()),
    StructField("hash", StringType()), # Note: 'hash' in output is not transaction hash, but script hash
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
features_df = features_df.withColumn("inputs_parsed", from_json(col("inputs"), input_array_schema)) \
                         .withColumn("out_parsed", from_json(col("out"), output_array_schema))

# UDF to sum values from parsed input/output arrays
def sum_values_from_parsed_array_udf(arr):
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

sum_values_pyspark_udf = udf(sum_values_from_parsed_array_udf, DoubleType())

features_df = features_df.withColumn("total_input_value", sum_values_pyspark_udf(col("inputs_parsed"))) \
                         .withColumn("total_output_value", sum_values_pyspark_udf(col("out_parsed")))

# Add dummy ML prediction columns for consistency with dashboard, but they will always be 0/false
features_df = features_df.withColumn("mlFraudScore", lit(0.0).cast(DoubleType()))
features_df = features_df.withColumn("mlPrediction", lit(0).cast(IntegerType()))
features_df = features_df.withColumn("isSmurfingRule", lit(False).cast(BooleanType()))
features_df = features_df.withColumn("shap_features_json", lit("{}").cast(StringType())) # Empty SHAP for Gemini only

# --- Define process_batch function for full processing including Neo4j and LLM ---
def process_batch(df, epoch_id):
    # Filter out records where 'hash' is null or empty before processing
    filtered_df = df.filter(col("hash").isNotNull() & (col("hash") != ""))

    if filtered_df.rdd.isEmpty():
        print(f"Batch {epoch_id}: No valid data after filtering or batch was empty.")
        return

    print(f"Batch {epoch_id}: Processing {filtered_df.count()} records for Neo4j/LLM.")

    # --- Write to Neo4j using foreachPartition ---
    def write_partition_to_neo4j(partition_rows):
        local_neo4j_driver = None
        try:
            local_neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD))
            with local_neo4j_driver.session() as session:
                rows_written_in_partition = 0
                for row in partition_rows: # Iterate over Python Row objects
                    rows_written_in_partition += 1
                    # Extract data from Spark Row object
                    tx_hash = row["hash"]
                    timestamp = row["time"]
                    vin_sz = row["vin_sz"]
                    vout_sz = row["vout_sz"]
                    size = row["size"]
                    fee = row["fee"]
                    fee_per_byte = row["fee_per_byte"]
                    total_input_value = row["total_input_value"]
                    total_output_value = row["total_output_value"]
                    
                    # For Gemini-only, ML/Smurfing values are always default
                    ml_fraud_score = 0.0 
                    is_smurfing_rule = False
                    shap_features_json = "{}"

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
                    inputs_json_str = row["inputs"] # Use the original string for parsing in executor
                    input_addresses_data = []
                    if inputs_json_str:
                        try:
                            input_addresses_data = json.loads(inputs_json_str)
                        except json.JSONDecodeError:
                            pass # Silently skip if JSON is malformed

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
                    out_json_str = row["out"] # Use the original string for parsing in executor
                    output_addresses_data = []
                    if out_json_str:
                        try:
                            output_addresses_data = json.loads(out_json_str)
                        except json.JSONDecodeError:
                            pass # Silently skip if JSON is malformed

                    if output_addresses_data:
                        for output_data in output_addresses_data:
                            if isinstance(output_data, dict) and 'addr' in output_data:
                                addr_id = output_data['addr']
                                if addr_id: # Ensure address is not None/empty
                                    session.run("""
                                        MERGE (a:Address {id: $addr_id})
                                        MERGE (t:Transaction {hash: $tx_hash})-[:SENT_TO]->(a)
                                        """, addr_id=addr_id, tx_hash=tx_hash)
                if rows_written_in_partition > 0:
                    print(f"Batch {epoch_id}: Partition processed {rows_written_in_partition} records to Neo4j.")
        except Exception as e:
            print(f"Batch {epoch_id}: Error writing partition to Neo4j: {e}", file=sys.stderr)
        finally:
            if local_neo4j_driver:
                local_neo4j_driver.close() # Close driver for each partition

    # Apply the function to each partition of the DataFrame
    filtered_df.foreachPartition(write_partition_to_neo4j)

    # --- Call LLM Service for Alerts ---
    # Convert to Pandas for iteration and LLM calls
    pandas_df = filtered_df.coalesce(1).toPandas() # Use coalesce(1) for small batches, but be aware of scalability

    if not pandas_df.empty:
        print(f"Batch {epoch_id}: Processing {len(pandas_df)} records for LLM analysis.")
        for index, row in pandas_df.iterrows():
            # You might define conditions here to call LLM, e.g., for certain transaction patterns
            # For now, we call LLM for every transaction to demonstrate flow.
            alert_data = {
                "transaction_hash": str(row["hash"]),
                "ml_fraud_score": float(row["mlFraudScore"]), # Will be 0.0
                "is_smurfing_rule": bool(row["isSmurfingRule"]), # Will be False
                "num_inputs": int(row["vin_sz"]),
                "num_outputs": int(row["vout_sz"]),
                "total_input_value": float(row["total_input_value"]),
                "total_output_value": float(row["total_output_value"]),
                "transaction_fee": int(row["fee"]),
                "fee_per_byte": float(row["fee_per_byte"]),
                "shap_features_json": str(row["shap_features_json"]) # Will be "{}"
            }
            try:
                response = requests.post(LLM_SERVICE_URL, json=alert_data, timeout=30)
                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                sar_response = response.json()
                print(f"LLM SAR Draft for {row['hash']}:\n{sar_response.get('sar_draft', 'No SAR generated.')}\n", file=sys.stderr)
            except requests.exceptions.RequestException as req_err:
                print(f"Batch {epoch_id}: Error calling LLM service for {row['hash']}: {req_err}", file=sys.stderr)
            except json.JSONDecodeError as json_err:
                print(f"Batch {epoch_id}: Error decoding JSON response from LLM service for {row['hash']}: {json_err}. Response: {response.text}", file=sys.stderr)
            except Exception as e:
                print(f"Batch {epoch_id}: An unexpected error occurred when calling LLM service for {row['hash']}: {e}", file=sys.stderr)
    else:
        print(f"Batch {epoch_id}: No transactions to send to LLM service.")

    print(f"Batch {epoch_id}: Completed processing cycle.")


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