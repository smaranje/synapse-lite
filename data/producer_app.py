# data/producer_app.py
import os
import time
import json
import random
import sys
from kafka import KafkaProducer

KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:9092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'transactions')

def generate_transaction_data():
    # Generate a dummy Bitcoin transaction
    tx_hash = ''.join(random.choices('0123456789abcdef', k=64))
    vin_sz = random.randint(1, 5)
    vout_sz = random.randint(1, 5)
    size = random.randint(200, 1000)
    fee = random.randint(1000, 50000)
    current_time = int(time.time())

    # Simplified inputs and outputs for demonstration
    inputs_list = []
    for _ in range(vin_sz):
        inputs_list.append({
            "prev_out": {
                "addr": ''.join(random.choices('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz', k=34)),
                "value": random.randint(100000, 100000000)
            }
        })
    
    outputs_list = []
    for _ in range(vout_sz):
        outputs_list.append({
            "addr": ''.join(random.choices('123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz', k=34)),
            "value": random.randint(100000, 100000000)
        })

    return {
        "hash": tx_hash,
        "ver": 1,
        "vin_sz": vin_sz,
        "vout_sz": vout_sz,
        "size": size,
        "weight": size * 4, # Approximation
        "fee": fee,
        "relayed_by": "0.0.0.0",
        "lock_time": 0,
        "tx_index": random.randint(1, 1000000),
        "double_spend": False,
        "time": current_time,
        "block_height": 0,
        "inputs": json.dumps(inputs_list), # Store as JSON string
        "out": json.dumps(outputs_list) # Store as JSON string
    }

def main():
    producer = None
    max_retries = 10
    retry_count = 0
    while producer is None and retry_count < max_retries:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(0, 10, 1) # Specify API version for compatibility
            )
            print(f"Kafka producer connected to {KAFKA_BROKER}")
        except Exception as e:
            print(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
            time.sleep(5)
            retry_count += 1
    
    if producer is None:
        print("Failed to connect to Kafka after multiple retries. Exiting.")
        sys.exit(1)

    while True:
        data = generate_transaction_data()
        try:
            future = producer.send(KAFKA_TOPIC, value=data)
            record_metadata = future.get(timeout=10)
            print(f"Producing record to topic '{record_metadata.topic}', partition {record_metadata.partition}, offset {record_metadata.offset}")
        except Exception as e:
            print(f"Error producing message: {e}")
            # Attempt to re-initialize producer if connection is lost
            producer.close()
            producer = None
            retry_count = 0
            while producer is None and retry_count < max_retries:
                try:
                    producer = KafkaProducer(
                        bootstrap_servers=KAFKA_BROKER.split(','),
                        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                        api_version=(0, 10, 1)
                    )
                    print(f"Reconnected Kafka producer to {KAFKA_BROKER}")
                except Exception as reconnect_e:
                    print(f"Failed to reconnect to Kafka: {reconnect_e}. Retrying in 5 seconds...")
                    time.sleep(5)
                    retry_count += 1
            if producer is None:
                print("Failed to reconnect to Kafka after multiple retries. Exiting.")
                sys.exit(1)

        time.sleep(1) # Produce a message every second

if __name__ == '__main__':
    main()