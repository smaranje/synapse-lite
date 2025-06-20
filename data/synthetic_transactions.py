# data/synthetic_transactions.py
import json
import time
import uuid
import random
from kafka import KafkaProducer

# Configuration for Kafka
# Note: 'kafka' is the service name defined in docker-compose.yml
# Docker's internal DNS allows us to resolve 'kafka' to its IP address.
KAFKA_BROKER = 'kafka:29092' # Internal Kafka address
KAFKA_TOPIC = 'transactions'

# Initialize Kafka Producer
# value_serializer converts Python dicts to JSON bytes for Kafka
try:
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1) # Specify API version for compatibility
    )
    print(f"Kafka Producer connected to {KAFKA_BROKER}")
except Exception as e:
    print(f"Error connecting to Kafka: {e}")
    exit(1) # Exit if connection fails

# --- Synthetic Data Generation Logic ---
# Simple data generation for demonstration.
# In a real scenario, this would be more sophisticated to simulate
# various transaction types and legitimate/fraudulent patterns.

# Define a pool of accounts for generating "smurfing" like patterns
# A few accounts that will repeatedly transact small amounts
smurfing_accounts_pool = [f"ACC_SMURF_{i:03d}" for i in range(10)]
normal_accounts_pool = [f"ACC_NORM_{i:03d}" for i in range(100, 500)]

def generate_transaction(is_smurfing=False):
    transaction_id = str(uuid.uuid4())
    amount = round(random.uniform(10.0, 5000.0), 2) # Most transactions under $10K
    transaction_type = random.choice(["transfer", "payment", "deposit", "withdrawal"])
    timestamp = int(time.time() * 1000) # Milliseconds

    if is_smurfing and smurfing_accounts_pool:
        # Simulate small, repeated transfers between a few accounts
        sender = random.choice(smurfing_accounts_pool)
        receiver = random.choice([acc for acc in smurfing_accounts_pool if acc != sender])
        amount = round(random.uniform(5.0, 99.0), 2) # Small amounts for smurfing
        transaction_type = "transfer"
    else:
        sender = random.choice(normal_accounts_pool)
        receiver = random.choice(normal_accounts_pool)
        while receiver == sender: # Ensure sender and receiver are different
            receiver = random.choice(normal_accounts_pool)

    transaction = {
        "transaction_id": transaction_id,
        "sender_account": sender,
        "receiver_account": receiver,
        "amount": amount,
        "currency": "USD",
        "timestamp": timestamp,
        "transaction_type": transaction_type
    }
    return transaction

# Main loop to generate and send transactions
if __name__ == "__main__":
    print(f"Starting to generate transactions and send to Kafka topic: {KAFKA_TOPIC}")
    try:
        while True:
            # Generate a mix of normal and potentially "smurfing" transactions
            # Adjust probability to control smurfing frequency
            is_smurfing_event = random.random() < 0.1 # 10% chance of a smurfing-like event
            transaction = generate_transaction(is_smurfing=is_smurfing_event)

            # Send transaction to Kafka
            future = producer.send(KAFKA_TOPIC, value=transaction)
            # Block until message is sent (for demo simplicity; in prod, might handle asynchronously)
            record_metadata = future.get(timeout=10)
            # print(f"Sent: {transaction['transaction_id']} from {transaction['sender_account']} to {transaction['receiver_account']} amount {transaction['amount']}")

            time.sleep(random.uniform(0.1, 0.5)) # Send 2-10 transactions per second
    except KeyboardInterrupt:
        print("\nStopping transaction generator.")
    finally:
        producer.close()
        print("Kafka Producer closed.")
