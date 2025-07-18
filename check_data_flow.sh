#!/bin/bash

# check_data_flow.sh - Simple Data Flow Status Check
# Easy way for users to see if data is flowing

echo "🔍 Checking Data Flow Status..."
echo "================================"

COMPOSE_FILE="docker-compose-robust.yml"

# Check if pipeline is running
if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
    echo "❌ Pipeline is not running"
    echo "💡 Start it with: ./start_robust_pipeline.sh"
    exit 1
fi

echo "✅ Pipeline is running"
echo

# Check data generator
echo "📊 Data Generator:"
recent_logs=$(docker-compose -f "$COMPOSE_FILE" logs --tail=5 data-generator 2>/dev/null | grep -E "(sent|Sent|messages_sent)" | tail -1)
if [ -n "$recent_logs" ]; then
    echo "✅ Generating transactions"
else
    echo "⏳ Starting up..."
fi

echo

# Check Spark processing
echo "⚡ Spark Processing:"
batch_logs=$(docker-compose -f "$COMPOSE_FILE" logs --tail=5 spark-app 2>/dev/null | grep -E "(batch|Processing)" | tail -1)
if [ -n "$batch_logs" ]; then
    echo "✅ Processing data"
else
    echo "⏳ Waiting for data..."
fi

echo

# Check Neo4j data
echo "🗄️ Database Storage:"
if command -v docker-compose &> /dev/null; then
    tx_count=$(docker-compose -f "$COMPOSE_FILE" exec neo4j cypher-shell -u neo4j -p password "MATCH (tx:Transaction) RETURN count(tx) as count;" 2>/dev/null | grep -o '[0-9]\+' | head -1 || echo "0")
    
    if [ "$tx_count" -gt 0 ]; then
        echo "✅ $tx_count transactions stored"
    else
        echo "⏳ No data yet (normal for new startup)"
    fi
else
    echo "⏳ Checking..."
fi

echo
echo "🎯 Data Flow Status:"

if [ -n "$recent_logs" ] && [ -n "$batch_logs" ] && [ "$tx_count" -gt 0 ]; then
    echo "🎉 Data is flowing perfectly!"
    echo "   • Generator → Kafka → Spark → Neo4j ✅"
elif [ -n "$recent_logs" ] && [ -n "$batch_logs" ]; then
    echo "🔄 Data is processing (may take 1-2 minutes to see in database)"
elif [ -n "$recent_logs" ]; then
    echo "⏳ Data is being generated, waiting for processing..."
else
    echo "🔧 Pipeline is starting up, please wait..."
fi

echo
echo "📱 Dashboard: http://localhost:8501"
echo "🔍 Neo4j Browser: http://localhost:7474"
echo
echo "🔄 Run this script again in 30 seconds to see updates"