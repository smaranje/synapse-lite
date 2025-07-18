# spark_app/streaming_app_robust.py - Robust Spark Streaming with Connection Resilience
import os
import sys
import json
import time
import logging
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, lit, udf, collect_list, struct
from pyspark.sql.types import (
    StructType, StringType, LongType, DoubleType, BooleanType, ArrayType, StructField, IntegerType
)
from neo4j import GraphDatabase, basic_auth
from neo4j.exceptions import ServiceUnavailable, TransientError
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment Variables with defaults
KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:9092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')
NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'password')
LLM_SERVICE_URL = os.environ.get('LLM_SERVICE_URL', 'http://flask-llm-service:5000/generate-sar')
BATCH_SIZE = int(os.environ.get('BATCH_SIZE', '100'))
LLM_BATCH_SIZE = int(os.environ.get('LLM_BATCH_SIZE', '10'))

# Retry configurations
KAFKA_CONNECTION_RETRIES = int(os.environ.get('KAFKA_CONNECTION_RETRIES', '20'))
NEO4J_CONNECTION_RETRIES = int(os.environ.get('NEO4J_CONNECTION_RETRIES', '15'))
LLM_CONNECTION_RETRIES = int(os.environ.get('LLM_CONNECTION_RETRIES', '10'))

class ConnectionManager:
    """Manages connections with retry logic and health checking"""
    
    @staticmethod
    def retry_with_backoff(func, max_retries: int, service_name: str, *args, **kwargs):
        """Generic retry function with exponential backoff"""
        backoff = 1.0
        for attempt in range(max_retries):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"Successfully connected to {service_name} after {attempt + 1} attempts")
                return result
            except Exception as e:
                logger.warning(f"Failed to connect to {service_name} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {backoff:.1f} seconds...")
                    time.sleep(backoff)
                    backoff = min(backoff * 1.5, 30.0)  # Cap at 30 seconds
                else:
                    logger.error(f"Failed to connect to {service_name} after {max_retries} attempts")
                    raise e

class RobustNeo4jConnectionPool:
    """Robust Neo4j connection pool with health checking and auto-reconnection"""
    
    def __init__(self, uri: str, auth: tuple, max_size: int = 50):
        self.uri = uri
        self.auth = auth
        self.max_size = max_size
        self.driver: Optional[GraphDatabase.driver] = None
        self._initialize_driver()
    
    def _initialize_driver(self):
        """Initialize Neo4j driver with retry logic"""
        def create_driver():
            driver = GraphDatabase.driver(
                self.uri,
                auth=self.auth,
                max_connection_pool_size=self.max_size,
                connection_acquisition_timeout=30.0,
                max_transaction_retry_time=30.0
            )
            # Test connection
            with driver.session() as session:
                session.run("RETURN 1")
            return driver
        
        self.driver = ConnectionManager.retry_with_backoff(
            create_driver,
            NEO4J_CONNECTION_RETRIES,
            "Neo4j"
        )
        logger.info("Neo4j connection pool initialized successfully")
    
    def get_session(self):
        """Get a session with health check"""
        if self.driver is None:
            self._initialize_driver()
        
        try:
            return self.driver.session()
        except (ServiceUnavailable, TransientError) as e:
            logger.warning(f"Neo4j session creation failed: {e}. Reinitializing driver...")
            self._initialize_driver()
            return self.driver.session()
    
    def execute_with_retry(self, query: str, parameters: Dict = None, max_retries: int = 3):
        """Execute query with retry logic"""
        for attempt in range(max_retries):
            try:
                with self.get_session() as session:
                    result = session.run(query, parameters or {})
                    return list(result)
            except Exception as e:
                logger.warning(f"Neo4j query failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise e
    
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.close()

class RobustHTTPClient:
    """HTTP client with retry logic for LLM service calls"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=LLM_CONNECTION_RETRIES,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def post(self, endpoint: str, data: Dict, timeout: int = 30) -> Dict:
        """Make POST request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"HTTP request failed to {url}: {e}")
            raise e

def wait_for_kafka_readiness(kafka_broker: str, topic: str, max_retries: int = KAFKA_CONNECTION_RETRIES):
    """Wait for Kafka to be ready and topic to exist"""
    def check_kafka():
        from kafka import KafkaConsumer
        from kafka.errors import KafkaError
        
        # Test basic connectivity
        consumer = KafkaConsumer(
            bootstrap_servers=kafka_broker.split(','),
            consumer_timeout_ms=10000,
            api_version=(0, 10, 1)
        )
        
        # Check if topic exists
        metadata = consumer.list_consumer_group_offsets()
        topics = consumer.topics()
        
        if topic not in topics:
            logger.warning(f"Topic '{topic}' not found. Available topics: {list(topics)}")
            # Topic might be auto-created, so this is not necessarily an error
        
        consumer.close()
        logger.info(f"Kafka is ready. Broker: {kafka_broker}, Topic: {topic}")
        return True
    
    return ConnectionManager.retry_with_backoff(
        check_kafka,
        max_retries,
        f"Kafka ({kafka_broker})"
    )

def create_spark_session_with_retry(app_name: str, max_retries: int = 5) -> SparkSession:
    """Create Spark session with retry logic"""
    def create_session():
        logger.info("Creating Spark session...")
        spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.6") \
            .config("spark.jars", "/app/neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoints") \
            .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("WARN")
        
        # Test Spark session
        test_df = spark.range(1).select(lit("test").alias("value"))
        test_df.collect()
        
        logger.info("Spark session created successfully")
        return spark
    
    return ConnectionManager.retry_with_backoff(
        create_session,
        max_retries,
        "Spark"
    )

def create_kafka_stream_with_retry(spark: SparkSession, kafka_broker: str, topic: str, max_retries: int = 5):
    """Create Kafka stream with retry logic"""
    def create_stream():
        logger.info(f"Creating Kafka stream from {kafka_broker} -> {topic}")
        
        kafka_df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_broker) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .option("maxOffsetsPerTrigger", str(BATCH_SIZE)) \
            .option("kafka.request.timeout.ms", "30000") \
            .option("kafka.session.timeout.ms", "30000") \
            .load()
        
        # Test the stream by checking if it can be created
        if kafka_df.isStreaming:
            logger.info("Kafka stream created successfully")
            return kafka_df
        else:
            raise Exception("Failed to create streaming DataFrame")
    
    return ConnectionManager.retry_with_backoff(
        create_stream,
        max_retries,
        f"Kafka Stream ({kafka_broker} -> {topic})"
    )

# Initialize global connections
logger.info("=== Robust Spark Streaming Application Starting ===")
logger.info(f"Configuration:")
logger.info(f"  Kafka Broker: {KAFKA_BROKER}")
logger.info(f"  Kafka Topic: {KAFKA_TOPIC}")
logger.info(f"  Neo4j URI: {NEO4J_URI}")
logger.info(f"  LLM Service: {LLM_SERVICE_URL}")
logger.info(f"  Batch Size: {BATCH_SIZE}")

# Wait for dependencies to be ready
logger.info("Waiting for dependencies to be ready...")
wait_for_kafka_readiness(KAFKA_BROKER, KAFKA_TOPIC)

# Initialize connections
neo4j_pool = RobustNeo4jConnectionPool(
    NEO4J_URI,
    basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD)
)

http_client = RobustHTTPClient(LLM_SERVICE_URL.rsplit('/', 1)[0])  # Remove endpoint from URL

# Create Spark session
spark = create_spark_session_with_retry("BitcoinFraudDetection_Robust")

# Define Kafka schema
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

# Define nested schemas for inputs and outputs
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
    StructField("script", StringType()),
    StructField("addr", StringType()),
    StructField("spent", BooleanType())
]))

def call_llm_service_robust(transaction_data: List[Dict]) -> str:
    """Call LLM service with robust error handling"""
    try:
        response = http_client.post('/generate-sar', {'transactions': transaction_data})
        return response.get('sar_report', 'No SAR report generated')
    except Exception as e:
        logger.error(f"LLM service call failed: {e}")
        return f"LLM service unavailable: {str(e)}"

def process_batch_robust(df, epoch_id):
    """Process batch with comprehensive error handling"""
    try:
        logger.info(f"Processing batch {epoch_id}")
        
        if df.rdd.isEmpty():
            logger.info(f"Batch {epoch_id} is empty, skipping")
            return
        
        count = df.count()
        logger.info(f"Batch {epoch_id}: Processing {count} records")
        
        # Collect transactions for processing
        transactions = df.collect()
        
        # Process in smaller batches for LLM service
        for i in range(0, len(transactions), LLM_BATCH_SIZE):
            batch_transactions = transactions[i:i + LLM_BATCH_SIZE]
            
            try:
                # Convert to format expected by LLM service
                transaction_data = []
                for row in batch_transactions:
                    tx_dict = row.asDict()
                    
                    # Parse JSON strings for inputs and outputs
                    try:
                        tx_dict['inputs'] = json.loads(tx_dict['inputs']) if tx_dict['inputs'] else []
                        tx_dict['out'] = json.loads(tx_dict['out']) if tx_dict['out'] else []
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON in transaction {tx_dict.get('hash', 'unknown')}: {e}")
                        tx_dict['inputs'] = []
                        tx_dict['out'] = []
                    
                    transaction_data.append(tx_dict)
                
                # Call LLM service
                sar_report = call_llm_service_robust(transaction_data)
                
                # Store results in Neo4j
                for tx_data in transaction_data:
                    store_transaction_in_neo4j(tx_data, sar_report)
                
                logger.info(f"Successfully processed {len(batch_transactions)} transactions in sub-batch")
                
            except Exception as e:
                logger.error(f"Error processing sub-batch: {e}")
                # Continue with next sub-batch
                continue
        
        logger.info(f"Batch {epoch_id} processing completed")
        
    except Exception as e:
        logger.error(f"Error in batch processing {epoch_id}: {e}")

def store_transaction_in_neo4j(tx_data: Dict, sar_report: str):
    """Store transaction in Neo4j with retry logic"""
    try:
        # Create transaction node
        create_tx_query = """
        MERGE (tx:Transaction {hash: $hash})
        SET tx.ver = $ver,
            tx.vin_sz = $vin_sz,
            tx.vout_sz = $vout_sz,
            tx.size = $size,
            tx.weight = $weight,
            tx.fee = $fee,
            tx.relayed_by = $relayed_by,
            tx.lock_time = $lock_time,
            tx.tx_index = $tx_index,
            tx.double_spend = $double_spend,
            tx.time = $time,
            tx.block_height = $block_height,
            tx.sar_report = $sar_report,
            tx.processed_at = datetime()
        """
        
        neo4j_pool.execute_with_retry(create_tx_query, {
            'hash': tx_data['hash'],
            'ver': tx_data['ver'],
            'vin_sz': tx_data['vin_sz'],
            'vout_sz': tx_data['vout_sz'],
            'size': tx_data['size'],
            'weight': tx_data['weight'],
            'fee': tx_data['fee'],
            'relayed_by': tx_data['relayed_by'],
            'lock_time': tx_data['lock_time'],
            'tx_index': tx_data['tx_index'],
            'double_spend': tx_data['double_spend'],
            'time': tx_data['time'],
            'block_height': tx_data['block_height'],
            'sar_report': sar_report
        })
        
        # Create address nodes and relationships
        for input_data in tx_data.get('inputs', []):
            if 'prev_out' in input_data and 'addr' in input_data['prev_out']:
                addr = input_data['prev_out']['addr']
                value = input_data['prev_out']['value']
                
                create_input_query = """
                MERGE (addr:Address {address: $address})
                MERGE (tx:Transaction {hash: $tx_hash})
                MERGE (addr)-[r:SENT_TO]->(tx)
                SET r.value = $value, r.type = 'input'
                """
                
                neo4j_pool.execute_with_retry(create_input_query, {
                    'address': addr,
                    'tx_hash': tx_data['hash'],
                    'value': value
                })
        
        for output_data in tx_data.get('out', []):
            if 'addr' in output_data:
                addr = output_data['addr']
                value = output_data['value']
                
                create_output_query = """
                MERGE (addr:Address {address: $address})
                MERGE (tx:Transaction {hash: $tx_hash})
                MERGE (tx)-[r:SENT_TO]->(addr)
                SET r.value = $value, r.type = 'output'
                """
                
                neo4j_pool.execute_with_retry(create_output_query, {
                    'address': addr,
                    'tx_hash': tx_data['hash'],
                    'value': value
                })
        
        logger.debug(f"Successfully stored transaction {tx_data['hash']} in Neo4j")
        
    except Exception as e:
        logger.error(f"Failed to store transaction {tx_data.get('hash', 'unknown')} in Neo4j: {e}")

def main():
    """Main streaming application"""
    try:
        logger.info("Starting Kafka stream creation...")
        
        # Create Kafka stream with retry
        kafka_df = create_kafka_stream_with_retry(spark, KAFKA_BROKER, KAFKA_TOPIC)
        
        # Parse the Kafka value (JSON string) into structured DataFrame
        logger.info("Setting up stream processing pipeline...")
        
        parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json_value") \
            .select(from_json(col("json_value"), schema).alias("data")) \
            .select("data.*")
        
        # Start the streaming query with robust error handling
        logger.info("Starting streaming query...")
        
        query = parsed_df.writeStream \
            .foreachBatch(process_batch_robust) \
            .outputMode("append") \
            .trigger(processingTime='10 seconds') \
            .option("checkpointLocation", "/tmp/checkpoints") \
            .start()
        
        logger.info("Streaming query started successfully. Waiting for termination...")
        
        # Wait for termination
        query.awaitTermination()
        
    except Exception as e:
        logger.error(f"Fatal error in streaming application: {e}")
        raise e
    finally:
        logger.info("Cleaning up resources...")
        if neo4j_pool:
            neo4j_pool.close()
        if spark:
            spark.stop()

if __name__ == '__main__':
    main()