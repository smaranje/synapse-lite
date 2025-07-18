#!/bin/bash

echo "=== Data Pipeline Debug Script ==="
echo ""

# Check if services are running
echo "1. Checking service health status:"
docker-compose -f docker-compose-optimized.yml ps

echo ""
echo "2. Checking Kafka topics:"
docker exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list

echo ""
echo "3. Checking if data is being produced to Kafka:"
echo "   (Waiting 5 seconds to collect messages...)"
timeout 5 docker exec kafka kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic transactions --from-beginning --max-messages 5

echo ""
echo "4. Checking Neo4j transaction count:"
docker exec neo4j cypher-shell -u neo4j -p password "MATCH (t:Transaction) RETURN count(t) as transaction_count"

echo ""
echo "5. Checking Neo4j address count:"
docker exec neo4j cypher-shell -u neo4j -p password "MATCH (a:Address) RETURN count(a) as address_count"

echo ""
echo "6. Checking Spark app logs (last 50 lines):"
docker logs spark-app-optimized --tail 50

echo ""
echo "7. Checking data generator logs (last 20 lines):"
docker logs data-generator --tail 20

echo ""
echo "8. Checking Kafka consumer group status:"
docker exec kafka kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

echo ""
echo "9. Memory usage of containers:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "=== Debug Complete ==="