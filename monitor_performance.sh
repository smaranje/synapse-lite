#!/bin/bash

# monitor_performance.sh - Monitor the performance of optimized data pipeline

echo "=== Performance Monitoring Dashboard ==="
echo "Monitoring optimized data engineering pipeline..."
echo ""

# Function to get container stats
get_container_stats() {
    local container=$1
    local stats=$(docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $container 2>/dev/null | tail -n 1)
    echo "$stats"
}

# Function to count Neo4j operations
count_neo4j_operations() {
    docker exec neo4j cypher-shell -u neo4j -p password "
    MATCH (t:Transaction)
    RETURN count(t) as transaction_count
    " 2>/dev/null | grep -E "[0-9]+" | tail -n 1
}

# Function to get Redis cache stats
get_redis_stats() {
    docker exec redis redis-cli INFO stats 2>/dev/null | grep -E "keyspace_hits|keyspace_misses" | tr '\r' ' '
}

# Function to check Kafka lag
check_kafka_lag() {
    docker exec kafka kafka-consumer-groups.sh \
        --bootstrap-server localhost:9092 \
        --group spark-kafka-consumer \
        --describe 2>/dev/null | grep -E "transactions.*[0-9]+" | awk '{print "Topic: "$1", Lag: "$5}'
}

# Monitoring loop
while true; do
    clear
    echo "=== Performance Monitoring Dashboard ==="
    echo "Time: $(date)"
    echo ""
    
    echo "=== Container Resource Usage ==="
    echo "Container                CPU%    Memory Usage"
    echo "------------------------------------------------"
    get_container_stats "spark-app-optimized"
    get_container_stats "neo4j"
    get_container_stats "redis"
    get_container_stats "flask-llm-service-optimized"
    get_container_stats "streamlit-dashboard-optimized"
    echo ""
    
    echo "=== Neo4j Statistics ==="
    tx_count=$(count_neo4j_operations)
    echo "Total Transactions: $tx_count"
    
    # Check write performance
    start_count=$tx_count
    sleep 5
    end_count=$(count_neo4j_operations)
    write_rate=$((($end_count - $start_count) * 12))  # per minute
    echo "Write Rate: ~$write_rate transactions/minute"
    echo ""
    
    echo "=== Redis Cache Performance ==="
    redis_stats=$(get_redis_stats)
    echo "$redis_stats"
    
    # Calculate hit rate
    hits=$(echo "$redis_stats" | grep -oP 'keyspace_hits:\K[0-9]+' || echo "0")
    misses=$(echo "$redis_stats" | grep -oP 'keyspace_misses:\K[0-9]+' || echo "0")
    if [ $((hits + misses)) -gt 0 ]; then
        hit_rate=$(awk "BEGIN {printf \"%.2f\", ($hits / ($hits + $misses)) * 100}")
        echo "Cache Hit Rate: ${hit_rate}%"
    fi
    echo ""
    
    echo "=== Kafka Performance ==="
    kafka_lag=$(check_kafka_lag)
    if [ -n "$kafka_lag" ]; then
        echo "$kafka_lag"
    else
        echo "No consumer lag information available"
    fi
    echo ""
    
    echo "=== Service Health Status ==="
    # Check service health
    services=("neo4j:7474" "flask-llm-service-optimized:5000/health" "streamlit-dashboard-optimized:8501/_stcore/health" "redis:6379")
    for service in "${services[@]}"; do
        IFS=':' read -r container port <<< "$service"
        if [ "$container" = "redis" ]; then
            if docker exec redis redis-cli ping > /dev/null 2>&1; then
                echo "✓ $container is healthy"
            else
                echo "✗ $container is not responding"
            fi
        else
            if curl -s -f "http://localhost:$port" > /dev/null 2>&1; then
                echo "✓ $container is healthy"
            else
                echo "✗ $container is not responding"
            fi
        fi
    done
    echo ""
    
    echo "=== Optimization Metrics ==="
    echo "• Batch Processing: Enabled (processing up to 100 records/batch)"
    echo "• Connection Pooling: Active (50 connections max)"
    echo "• Async LLM Processing: Enabled (10 transactions/batch)"
    echo "• Redis Caching: Active (5-minute TTL)"
    echo ""
    
    echo "Press Ctrl+C to exit. Refreshing in 10 seconds..."
    sleep 10
done