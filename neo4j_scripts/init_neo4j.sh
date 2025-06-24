#!/bin/bash
# neo4j_scripts/init_neo4j.sh
# Script to initialize Neo4j with constraints and indexes.

NEO4J_URI=${NEO4J_URI:-"bolt://neo4j:7687"}
NEO4J_USERNAME=${NEO4J_USERNAME:-"neo4j"}
NEO4J_PASSWORD=${NEO4J_PASSWORD:-"password"}

echo "Waiting for Neo4j to be available at ${NEO4J_URI}..."
# Wait for Neo4j to be ready
/var/lib/neo4j/bin/neo4j-admin server status --uri="${NEO4J_URI}" --auth="${NEO4J_USERNAME}/${NEO4J_PASSWORD}" --wait-for-server=60s

if [ $? -ne 0 ]; then
    echo "Neo4j did not start in time. Exiting."
    exit 1
fi

echo "Neo4j is up. Running initialization scripts..."

# Run Cypher scripts to create constraints and indexes
# Add constraints for nodes to ensure uniqueness and optimize lookups
# These are crucial for graph performance and data integrity
cypher-shell -a "${NEO4J_URI}" -u "${NEO4J_USERNAME}" -p "${NEO4J_PASSWORD}" "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Address) REQUIRE a.id IS UNIQUE;"
if [ $? -ne 0 ]; then echo "Error creating Address ID constraint. Continuing..."; fi

cypher-shell -a "${NEO4J_URI}" -u "${NEO4J_USERNAME}" -p "${NEO4J_PASSWORD}" "CREATE CONSTRAINT IF NOT EXISTS FOR (tx:Transaction) REQUIRE tx.hash IS UNIQUE;"
if [ $? -ne 0 ]; then echo "Error creating Transaction Hash constraint. Continuing..."; fi

echo "Neo4j initialization complete."
