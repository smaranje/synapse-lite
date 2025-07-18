#!/bin/bash

# Script to fix Streamlit dashboard to use real data instead of dummy data

echo "=== Step 1: Stopping streamlit-dashboard container ==="
docker compose stop streamlit-dashboard

echo -e "\n=== Step 2: Restarting with override configuration ==="
# The docker-compose.override.yml file has been created with USE_DUMMY_DATA=false
docker compose down streamlit-dashboard
docker compose up -d streamlit-dashboard

echo -e "\n=== Step 3: Verifying the change ==="
echo "Checking USE_DUMMY_DATA environment variable:"
docker exec streamlit-dashboard env | grep USE_DUMMY_DATA

echo -e "\nChecking streamlit-dashboard logs:"
docker compose logs streamlit-dashboard --tail=20

echo -e "\n=== Step 4: Starting data generator ==="
# Start data generator without waiting for health checks
docker compose up -d --no-deps data-generator

echo -e "\nChecking data generator logs:"
docker compose logs data-generator --tail=30

echo -e "\n=== Step 5: Populating Neo4j with sample data ==="
# Create sample transactions in Neo4j
docker exec -i neo4j cypher-shell -u neo4j -p password << 'EOF'
CREATE (t1:Transaction {
  hash: 'abc123def456',
  timestamp: datetime(),
  total_value_btc: 1.5,
  total_value_usd: 67500,
  ml_score: 0.75,
  risk_level: 'High',
  fee: 0.0001,
  num_inputs: 2,
  num_outputs: 3
})
CREATE (t2:Transaction {
  hash: 'xyz789ghi012',
  timestamp: datetime(),
  total_value_btc: 0.5,
  total_value_usd: 22500,
  ml_score: 0.25,
  risk_level: 'Low',
  fee: 0.00005,
  num_inputs: 1,
  num_outputs: 2
})
CREATE (t3:Transaction {
  hash: 'def456ghi789',
  timestamp: datetime(),
  total_value_btc: 2.3,
  total_value_usd: 103500,
  ml_score: 0.90,
  risk_level: 'Critical',
  fee: 0.0002,
  num_inputs: 5,
  num_outputs: 8
})
CREATE (t4:Transaction {
  hash: 'jkl012mno345',
  timestamp: datetime(),
  total_value_btc: 0.1,
  total_value_usd: 4500,
  ml_score: 0.15,
  risk_level: 'Low',
  fee: 0.00002,
  num_inputs: 1,
  num_outputs: 1
})
RETURN t1, t2, t3, t4;
EOF

echo -e "\n=== Step 6: Final status check ==="
echo "All services status:"
docker compose ps

echo -e "\n=== Setup Complete! ==="
echo "1. Access Streamlit dashboard at: http://localhost:8501"
echo "2. Check the sidebar - you should see service status indicators with ✓"
echo "3. The dashboard should now display real data from Neo4j and Kafka"
echo "4. If you see any issues, check the logs with: docker compose logs -f streamlit-dashboard"