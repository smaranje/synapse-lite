# neo4j_scripts/Dockerfile
# This Dockerfile is used to create a lightweight image
# that includes the Neo4j Shell (cypher-shell) for initialization scripts.

# Use a Neo4j image as the base, as it already includes cypher-shell.
FROM neo4j:5.19.0-community

# Set the working directory inside the container.
WORKDIR /app

# Copy the init_neo4j.sh script into the container.
COPY init_neo4j.sh .

# Copy the cypher_scripts directory (containing your .cypher files)
COPY cypher_scripts /cypher_scripts

# Make the initialization script executable.
RUN chmod +x init_neo4j.sh

# No specific CMD or ENTRYPOINT is set here, as the command to run
# the initialization script is defined directly in docker-compose.yml (neo4j-initializer service)
