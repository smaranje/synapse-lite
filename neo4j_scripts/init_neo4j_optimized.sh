#!/bin/bash

# neo4j_scripts/init_neo4j_optimized.sh - Optimized Neo4j initialization

echo "Waiting for Neo4j to be ready..."
until cypher-shell -a bolt://neo4j:7687 -u neo4j -p password "RETURN 1" > /dev/null 2>&1; do
    echo "Neo4j is not ready yet. Retrying in 5 seconds..."
    sleep 5
done

echo "Neo4j is ready. Creating optimized schema..."

# Create constraints and indexes for better performance
cypher-shell -a bolt://neo4j:7687 -u neo4j -p password << 'EOF'
// Create constraints for unique identifiers
CREATE CONSTRAINT transaction_hash_unique IF NOT EXISTS FOR (t:Transaction) REQUIRE t.hash IS UNIQUE;
CREATE CONSTRAINT address_id_unique IF NOT EXISTS FOR (a:Address) REQUIRE a.id IS UNIQUE;

// Create indexes for frequently queried properties
CREATE INDEX transaction_timestamp IF NOT EXISTS FOR (t:Transaction) ON (t.timestamp);
CREATE INDEX transaction_risk_score IF NOT EXISTS FOR (t:Transaction) ON (t.riskScore);
CREATE INDEX transaction_ml_score IF NOT EXISTS FOR (t:Transaction) ON (t.mlFraudScore);
CREATE INDEX transaction_fee IF NOT EXISTS FOR (t:Transaction) ON (t.fee);
CREATE INDEX transaction_total_value IF NOT EXISTS FOR (t:Transaction) ON (t.totalOutputValue);

// Create composite indexes for complex queries
CREATE INDEX transaction_risk_timestamp IF NOT EXISTS FOR (t:Transaction) ON (t.riskScore, t.timestamp);

// Create fulltext search index for transaction hashes
CREATE FULLTEXT INDEX transaction_hash_search IF NOT EXISTS FOR (t:Transaction) ON EACH [t.hash];

// Configure query cache and memory settings
CALL dbms.setConfigValue('dbms.query_cache_size', '100');

// Create some initial test data if database is empty
MATCH (t:Transaction)
WITH count(t) as txCount
WHERE txCount = 0
UNWIND range(1, 5) as i
CREATE (t:Transaction {
    hash: 'test_tx_' + toString(i),
    timestamp: timestamp() - (i * 3600000),
    fee: 1000 * i,
    feePerByte: 10 * i,
    totalInputValue: 100000 * i,
    totalOutputValue: 99000 * i,
    vin_sz: i,
    vout_sz: i + 1,
    size: 250 * i,
    mlFraudScore: toFloat(i) / 10.0,
    isSmurfingRule: i % 2 = 0,
    riskScore: toFloat(i) / 10.0
})
CREATE (a1:Address {id: 'addr_sender_' + toString(i)})
CREATE (a2:Address {id: 'addr_receiver_' + toString(i)})
CREATE (a1)-[:SENT]->(t)-[:SENT_TO]->(a2);

// Return schema information
CALL db.indexes() YIELD name, state, type
RETURN name, state, type;

CALL db.constraints() YIELD name, description
RETURN name, description;
EOF

echo "Neo4j optimization complete!"
echo "Created constraints, indexes, and sample data (if database was empty)"