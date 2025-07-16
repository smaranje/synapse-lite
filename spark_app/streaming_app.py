from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StringType

# Initialize Spark session
print("Initializing Spark Session...")
spark = SparkSession.builder \
    .appName("BitcoinFraudDetectionMinimal") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.6") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
print("Spark Session initialized.")

# Kafka settings
KAFKA_BROKER = "kafka:29092"
KAFKA_TOPIC = "transactions"

# Read from Kafka as raw string
print(f"Reading from Kafka topic '{KAFKA_TOPIC}' on broker '{KAFKA_BROKER}'...")
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .option("failOnDataLoss", "false") \
    .load()

# Select only the raw value
raw_df = kafka_df.select(col("value").cast("string").alias("raw_value"))

# Process batch
def process_batch(df, epoch_id):
    print(f"Batch {epoch_id}: Processing...")
    def print_row(row):
        print(f"Raw Kafka Message: {row['raw_value']}")
    
    df.foreach(print_row)
    print(f"Batch {epoch_id}: Completed.")

# Start streaming query
print("Starting Spark streaming query...")
query = raw_df.writeStream \
    .outputMode("append") \
    .foreachBatch(process_batch) \
    .trigger(processingTime="10 seconds") \
    .start()

query.awaitTermination()