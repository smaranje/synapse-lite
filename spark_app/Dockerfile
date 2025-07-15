FROM bitnami/spark:3.5.0

WORKDIR /app

# Switch to root user to perform privileged operations
USER root

# Fix APT environment by creating necessary directories and installing packages
RUN mkdir -p /var/lib/apt/lists/partial && \
    apt-get update && \
    apt-get install -y --no-install-recommends netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user for Spark (Bitnami images might already have 'spark' user)
RUN groupadd -g 1337 spark && useradd -m -u 1337 -g spark spark

# Switch back to the non-root 'spark' user for subsequent commands
USER spark

# Copy Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application files (streaming_app.py, model.py, fraud_rules.py)
COPY streaming_app.py model.py fraud_rules.py ./

# Copy the Neo4j Spark Connector JAR to the /app directory
COPY neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar /app/

# Make the main script executable
RUN chmod +x streaming_app.py