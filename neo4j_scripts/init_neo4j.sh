#!/bin/bash
# neo4j_scripts/init_neo4j.sh
# Script to initialize Neo4j with constraints and indexes.

NEO4J_URI=${NEO4J_URI:-"bolt://neo4j:7687"}
NEO4J_USERNAME=${NEO4J_USERNAME:-"neo4j"}
NEO4J_PASSWORD=${NEO4J_PASSWORD:-"password"}

# Extract host and port from NEO4J_URI for netcat check
NEO4J_HOST=$(echo $NEO4J_URI | sed -e 's|bolt://||g' -e 's|:.*||g')
NEO4J_PORT=$(echo $NEO4J_URI | sed -e 's|.*:||g')

echo "Waiting for Neo4j to be available at ${NEO4J_HOST}:${NEO4J_PORT}..."

# Wait for Neo4j's Bolt port to be open using netcat (nc)
# The healthcheck in docker-compose.yml for neo4j service should ideally handle this,
# but this provides an additional layer of robustness for the initializer script.
until nc -z ${NEO4J_HOST} ${NEO4J_PORT}; do
  echo "Still waiting for Neo4j Bolt port ${NEO4J_PORT}..."
  sleep 5
done

echo "Neo4j Bolt port is open. Running initialization scripts..."

# Run Cypher scripts to create constraints and indexes
# Add constraints for nodes to ensure uniqueness and optimize lookups
# These are crucial for graph performance and data integrity
cypher-shell -a "${NEO4J_URI}" -u "${NEO4J_USERNAME}" -p "${NEO4J_PASSWORD}" "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Address) REQUIRE a.id IS UNIQUE;"
if [ $? -ne 0 ]; then echo "Error creating Address ID constraint. Continuing..."; fi

cypher-shell -a "${NEO4J_URI}" -u "${NEO4J_USERNAME}" -p "${NEO4J_PASSWORD}" "CREATE CONSTRAINT IF NOT EXISTS FOR (tx:Transaction) REQUIRE tx.hash IS UNIQUE;"
if [ $? -ne 0 ]; then echo "Error creating Transaction Hash constraint. Continuing..."; fi

echo "Neo4j initialization complete."
