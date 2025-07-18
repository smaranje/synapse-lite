FROM bitnami/neo4j:5.26.9         # or the tag you’re using
WORKDIR /app

# optional: netcat, etc.
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# ───────────────────────────────────────────────────────────────
# 1. copy with the name you’ll run
COPY init_neo4j_optimized.sh /app/init_neo4j.sh
# 2. make it executable
RUN chmod +x /app/init_neo4j.sh
# 3. run it
ENTRYPOINT ["/app/init_neo4j.sh"]

