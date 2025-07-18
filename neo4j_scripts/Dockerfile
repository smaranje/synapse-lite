# neo4j_scripts/Dockerfile
FROM bitnami/neo4j:5.26.9                   # same base you already use

WORKDIR /app

# copy the one script you have
COPY init_neo4j_optimized.sh .

# ensure it is executable *inside the image*
RUN chmod +x /app/init_neo4j_optimized.sh

# run it when the container starts
ENTRYPOINT ["/bin/bash", "/app/init_neo4j_optimized.sh"]

