# data/producer_app.py
import os
import sys
import json
import time
from kafka import KafkaProducer

KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:29092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')

def create_kafka_producer():
    """Creates and returns a KafkaProducer instance."""
    retries = 5
    for i in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(0, 10, 1) # Specify Kafka API version
            )
            print(f"Kafka producer connected to {KAFKA_BROKER}")
            return producer
        except Exception as e:
            print(f"Attempt {i+1}/{retries}: Could not connect to Kafka broker at {KAFKA_BROKER}. Error: {e}")
            time.sleep(5) # Wait before retrying
    print("Failed to connect to Kafka producer after multiple retries. Exiting.")
    sys.exit(1)

def produce_messages():
    """Reads JSON from stdin and produces messages to Kafka."""
    producer = create_kafka_producer()
    if not producer:
        return

    print(f"Starting to produce messages to Kafka topic: {KAFKA_TOPIC}")
    # CRITICAL FIX: Add a continuous loop
    while True:
        line = sys.stdin.readline() # Read one line at a time
        if not line:
            # If stdin is closed, break the loop. For continuous data, stdin should remain open.
            print("Stdin closed. Stopping data production.")
            break
        try:
            data = json.loads(line.strip())
            producer.send(KAFKA_TOPIC, value=data)
            # print(f"Produced message to Kafka: {data.get('hash', 'N/A')}")
        except json.JSONDecodeError as e:
            print(f"Skipping invalid JSON line: {line.strip()}. Error: {e}")
        except Exception as e:
            print(f"Error producing message: {e}")
        time.sleep(0.1) # Small delay to avoid overwhelming Kafka

    producer.flush()
    # producer.close() # Keep producer open for continuous streaming
    print("Finished producing messages (if stdin closed).")

if __name__ == "__main__":
    produce_messages()

