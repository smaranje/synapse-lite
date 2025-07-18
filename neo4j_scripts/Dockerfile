# neo4j_scripts/Dockerfile  (use this exact path in your repo)

FROM neo4j:5.26.9-community      # matches the tag you already pulled
WORKDIR /app

# Optional: tiny util that’s handy for “nc”‑style checks
RUN apt-get update \
    && apt-get install -y --no-install-recommends netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy the single init script (no renaming)
COPY init_neo4j_optimized.sh /app/

# Make sure it’s executable
RUN chmod +x /app/init_neo4j_optimized.sh

# Run it and exit
ENTRYPOINT ["/app/init_neo4j_optimized.sh"]

