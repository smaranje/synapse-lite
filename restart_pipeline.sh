#!/bin/bash

echo "=== Restarting Data Pipeline with Fixes ==="
echo ""

# Stop all services
echo "1. Stopping all services..."
docker-compose -f docker-compose-optimized.yml down

# Remove any stale volumes or data that might cause issues
echo ""
echo "2. Cleaning up stale data..."
docker volume prune -f

# Start services in the correct order
echo ""
echo "3. Starting infrastructure services (Zookeeper, Kafka, Neo4j, Redis)..."
docker-compose -f docker-compose-optimized.yml up -d zookeeper redis

# Wait for Zookeeper to be ready
echo "   Waiting for Zookeeper to be ready..."
sleep 10

# Start Kafka
echo "4. Starting Kafka..."
docker-compose -f docker-compose-optimized.yml up -d kafka

# Wait for Kafka to be healthy
echo "   Waiting for Kafka to be healthy..."
while [ "$(docker inspect -f '{{.State.Health.Status}}' kafka 2>/dev/null)" != "healthy" ]; do
    echo "   Kafka is not healthy yet, waiting..."
    sleep 5
done
echo "   Kafka is healthy!"

# Initialize Kafka topic
echo ""
echo "5. Initializing Kafka topic..."
docker-compose -f docker-compose-optimized.yml up -d kafka-topic-initializer

# Start Neo4j
echo ""
echo "6. Starting Neo4j..."
docker-compose -f docker-compose-optimized.yml up -d neo4j

# Wait for Neo4j to be healthy
echo "   Waiting for Neo4j to be healthy..."
while [ "$(docker inspect -f '{{.State.Health.Status}}' neo4j 2>/dev/null)" != "healthy" ]; do
    echo "   Neo4j is not healthy yet, waiting..."
    sleep 5
done
echo "   Neo4j is healthy!"

# Initialize Neo4j
echo ""
echo "7. Initializing Neo4j schema..."
docker-compose -f docker-compose-optimized.yml up -d neo4j-initializer

# Start Spark
echo ""
echo "8. Starting Spark services..."
docker-compose -f docker-compose-optimized.yml up -d spark-master spark-worker

# Start Flask LLM service
echo ""
echo "9. Starting Flask LLM service..."
docker-compose -f docker-compose-optimized.yml up -d flask-llm-service-optimized

# Wait for Flask to be healthy
echo "   Waiting for Flask service to be healthy..."
while [ "$(docker inspect -f '{{.State.Health.Status}}' flask-llm-service-optimized 2>/dev/null)" != "healthy" ]; do
    echo "   Flask service is not healthy yet, waiting..."
    sleep 5
done
echo "   Flask service is healthy!"

# Start data generator
echo ""
echo "10. Starting data generator..."
docker-compose -f docker-compose-optimized.yml up -d data-generator

# Give data generator time to produce some messages
echo "    Waiting for data to be generated..."
sleep 10

# Start Spark streaming app
echo ""
echo "11. Starting Spark streaming application..."
docker-compose -f docker-compose-optimized.yml up -d spark-app-optimized

# Start Streamlit dashboard
echo ""
echo "12. Starting Streamlit dashboard..."
docker-compose -f docker-compose-optimized.yml up -d streamlit-dashboard-optimized

echo ""
echo "=== All services started! ==="
echo ""
echo "Waiting 20 seconds for data to flow through the pipeline..."
sleep 20

echo ""
echo "Running diagnostics..."
./debug_pipeline.sh