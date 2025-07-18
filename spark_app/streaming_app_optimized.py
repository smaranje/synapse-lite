# spark_app/streaming_app_optimized.py - Optimized Gemini-Only Fraud Analysis
import os
import sys
import json
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, lit, udf, collect_list, struct
from pyspark.sql.types import (
    StructType, StringType, LongType, DoubleType, BooleanType, ArrayType, StructField, IntegerType
)
from neo4j import GraphDatabase, basic_auth
import time

# --- Environment Variables ---
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:29092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')
NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'password')
LLM_SERVICE_URL = os.environ.get('LLM_SERVICE_URL', 'http://flask-llm-service:5000/generate-sar')
BATCH_SIZE = int(os.environ.get('BATCH_SIZE', '100'))
LLM_BATCH_SIZE = int(os.environ.get('LLM_BATCH_SIZE', '10'))

# --- Connection Pool for Neo4j ---
class Neo4jConnectionPool:
    def __init__(self, uri, auth, max_size=50):
        self.driver = GraphDatabase.driver(
            uri, 
            auth=auth,
            max_connection_pool_size=max_size,
            connection_acquisition_timeout=30.0
        )
    
    def get_session(self):
        return self.driver.session()
    
    def close(self):
        self.driver.close()

# Initialize connection pool
neo4j_pool = None
print(f"Initializing Neo4j connection pool for {NEO4J_URI}...")
for i in range(10):
    try:
        neo4j_pool = Neo4jConnectionPool(
            NEO4J_URI, 
            basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        # Test connection
        with neo4j_pool.get_session() as session:
            session.run("RETURN 1")
        print("Neo4j connection pool initialized successfully.")
        break
    except Exception as e:
        print(f"Neo4j connection attempt {i+1}/10 failed: {e}. Retrying in 10 seconds...", file=sys.stderr)
        time.sleep(10)

if not neo4j_pool:
    print("Failed to connect to Neo4j after multiple retries. Exiting.", file=sys.stderr)
    sys.exit(1)

# --- Spark Session Initialization ---
print("Initializing Spark Session...")
spark = SparkSession.builder \
    .appName("BitcoinFraudDetection_Optimized") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.6") \
    .config("spark.jars", "/app/neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print("Spark Session initialized.")

# --- Define Kafka Schema ---
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

# --- Async LLM Service Handler ---
async def call_llm_batch_async(batch_data):
    """Asynchronously call LLM service with batched data"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{LLM_SERVICE_URL}/batch",  # Assuming batch endpoint exists
                json={"transactions": batch_data},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"LLM service returned status {response.status}", file=sys.stderr)
                    return None
        except Exception as e:
            print(f"Error calling LLM service: {e}", file=sys.stderr)
            return None

# --- Read Data from Kafka ---
print(f"Reading from Kafka topic '{KAFKA_TOPIC}' on broker '{KAFKA_BROKER}'...")
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .option("maxOffsetsPerTrigger", BATCH_SIZE) \
    .load()

# Parse JSON and extract features
parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json_value") \
    .select(from_json(col("json_value"), schema).alias("data")) \
    .select("data.*")

# Feature engineering with optimized parsing
features_df = parsed_df.withColumn("fee_per_byte", col("fee") / col("size")) \
    .withColumn("mlFraudScore", lit(0.0).cast(DoubleType())) \
    .withColumn("mlPrediction", lit(0).cast(IntegerType())) \
    .withColumn("isSmurfingRule", lit(False).cast(BooleanType())) \
    .withColumn("shap_features_json", lit("{}").cast(StringType()))

# --- Optimized Batch Processing ---
def process_batch_optimized(df, epoch_id):
    """Optimized batch processing with connection pooling and batched operations"""
    
    # Filter valid records
    filtered_df = df.filter(col("hash").isNotNull() & (col("hash") != ""))
    
    if filtered_df.rdd.isEmpty():
        print(f"Batch {epoch_id}: No valid data to process.")
        return
    
    # Collect data for batch processing
    batch_data = filtered_df.collect()
    print(f"Batch {epoch_id}: Processing {len(batch_data)} records.")
    
    # Prepare batch for Neo4j
    neo4j_batch = []
    llm_batch = []
    
    for row in batch_data:
        # Parse inputs and outputs once
        inputs_data = []
        outputs_data = []
        
        try:
            if row["inputs"]:
                inputs_data = json.loads(row["inputs"])
        except json.JSONDecodeError:
            pass
        
        try:
            if row["out"]:
                outputs_data = json.loads(row["out"])
        except json.JSONDecodeError:
            pass
        
        # Calculate total values
        total_input_value = sum(
            input_data.get('prev_out', {}).get('value', 0) 
            for input_data in inputs_data 
            if isinstance(input_data, dict)
        )
        
        total_output_value = sum(
            output_data.get('value', 0) 
            for output_data in outputs_data 
            if isinstance(output_data, dict)
        )
        
        # Prepare transaction data
        tx_data = {
            "hash": row["hash"],
            "props": {
                "mlFraudScore": 0.0,
                "isSmurfingRule": False,
                "timestamp": row["time"],
                "vin_sz": row["vin_sz"],
                "vout_sz": row["vout_sz"],
                "size": row["size"],
                "fee": row["fee"],
                "feePerByte": row["fee_per_byte"],
                "totalInputValue": total_input_value,
                "totalOutputValue": total_output_value,
                "shapFeaturesJson": "{}"
            },
            "inputs": [
                input_data.get('prev_out', {}).get('addr')
                for input_data in inputs_data
                if isinstance(input_data, dict) and 
                input_data.get('prev_out', {}).get('addr')
            ],
            "outputs": [
                output_data.get('addr')
                for output_data in outputs_data
                if isinstance(output_data, dict) and output_data.get('addr')
            ]
        }
        
        neo4j_batch.append(tx_data)
        
        # Prepare LLM data
        llm_batch.append({
            "transaction_hash": row["hash"],
            "ml_fraud_score": 0.0,
            "is_smurfing_rule": False,
            "num_inputs": row["vin_sz"],
            "num_outputs": row["vout_sz"],
            "total_input_value": total_input_value,
            "total_output_value": total_output_value,
            "transaction_fee": row["fee"],
            "fee_per_byte": row["fee_per_byte"],
            "shap_features_json": "{}"
        })
    
    # Batch write to Neo4j
    write_batch_to_neo4j(neo4j_batch, epoch_id)
    
    # Async batch call to LLM service
    if llm_batch:
        asyncio.run(process_llm_batch(llm_batch, epoch_id))
    
    print(f"Batch {epoch_id}: Completed processing.")

def write_batch_to_neo4j(batch_data, epoch_id):
    """Write batch data to Neo4j using optimized Cypher query"""
    if not batch_data:
        return
    
    # Optimized Cypher query that processes entire batch in one go
    batch_query = """
    UNWIND $batch as tx
    MERGE (t:Transaction {hash: tx.hash})
    SET t += tx.props
    WITH t, tx
    UNWIND tx.inputs as input_addr
    MERGE (a:Address {id: input_addr})
    MERGE (a)-[:SENT]->(t)
    WITH t, tx
    UNWIND tx.outputs as output_addr
    MERGE (b:Address {id: output_addr})
    MERGE (t)-[:SENT_TO]->(b)
    """
    
    try:
        with neo4j_pool.get_session() as session:
            # Process in smaller chunks if batch is too large
            chunk_size = 50
            for i in range(0, len(batch_data), chunk_size):
                chunk = batch_data[i:i + chunk_size]
                session.run(batch_query, batch=chunk)
                print(f"Batch {epoch_id}: Written {min(i + chunk_size, len(batch_data))}/{len(batch_data)} transactions to Neo4j")
    except Exception as e:
        print(f"Batch {epoch_id}: Error writing to Neo4j: {e}", file=sys.stderr)

async def process_llm_batch(llm_batch, epoch_id):
    """Process LLM requests in batches asynchronously"""
    # Process in batches
    for i in range(0, len(llm_batch), LLM_BATCH_SIZE):
        batch = llm_batch[i:i + LLM_BATCH_SIZE]
        result = await call_llm_batch_async(batch)
        if result:
            print(f"Batch {epoch_id}: Processed {len(batch)} transactions through LLM service")
            # Store results back to Neo4j if needed
            if 'results' in result:
                store_llm_results(result['results'], epoch_id)

def store_llm_results(results, epoch_id):
    """Store LLM analysis results back to Neo4j"""
    if not results:
        return
    
    update_query = """
    UNWIND $results as result
    MATCH (t:Transaction {hash: result.transaction_hash})
    SET t.llmAnalysis = result.analysis,
        t.riskScore = result.risk_score,
        t.sarDraft = result.sar_draft
    """
    
    try:
        with neo4j_pool.get_session() as session:
            session.run(update_query, results=results)
            print(f"Batch {epoch_id}: Updated {len(results)} transactions with LLM analysis")
    except Exception as e:
        print(f"Batch {epoch_id}: Error updating LLM results: {e}", file=sys.stderr)

# Start the streaming query with optimized settings
print("Starting optimized Spark streaming query...")
query = features_df \
    .writeStream \
    .outputMode("append") \
    .foreachBatch(process_batch_optimized) \
    .trigger(processingTime="10 seconds") \
    .option("checkpointLocation", "/tmp/checkpoint") \
    .start()

print("Spark streaming query started. Awaiting termination...")
query.awaitTermination()

# Cleanup
if neo4j_pool:
    neo4j_pool.close()