FROM bitnami/spark:3.5.0

WORKDIR /app

# Switch to root user to perform privileged operations
USER root

# Fix APT environment by creating necessary directories and installing packages
RUN mkdir -p /var/lib/apt/lists/partial && \
    apt-get update && \
    apt-get install -y --no-install-recommends netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies as root
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application files with correct ownership
COPY --chown=spark:spark streaming_app.py model.py fraud_rules.py /app/

# Copy the Neo4j Spark Connector JAR with correct ownership
COPY --chown=spark:spark neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar /app/

# Make the main script executable as root
RUN chmod +x /app/streaming_app.py

# Switch to the 'spark' user for running the application
USER spark