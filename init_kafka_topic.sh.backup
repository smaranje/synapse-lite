#!/bin/bash

# init_kafka_topic.sh - Initialize Kafka topics

echo "Waiting for Kafka to be ready..."
until kafka-topics.sh --bootstrap-server kafka:9092 --list > /dev/null 2>&1; do
    echo "Kafka is not ready yet. Retrying in 5 seconds..."
    sleep 5
done

echo "Kafka is ready. Creating topics..."

# Create transactions topic with 4 partitions for better parallelism
kafka-topics.sh --bootstrap-server kafka:9092 \
    --create \
    --if-not-exists \
    --topic transactions \
    --partitions 4 \
    --replication-factor 1 \
    --config retention.ms=86400000 \
    --config compression.type=lz4

# Verify topic creation
echo "Verifying topic creation..."
kafka-topics.sh --bootstrap-server kafka:9092 --describe --topic transactions

echo "Kafka topic initialization complete!"