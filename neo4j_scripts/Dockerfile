# neo4j_scripts/Dockerfile
# This Dockerfile is used to build the neo4j-initializer image.

FROM neo4j:5.19.0-community

WORKDIR /app

# Install netcat for robust health checks in init_neo4j.sh
# Using apt-get for Debian-based images (like Neo4j's base)
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

COPY init_neo4j.sh .
COPY cypher_scripts /cypher_scripts

RUN chmod +x init_neo4j.sh
