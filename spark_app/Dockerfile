# spark_app/Dockerfile
FROM bitnami/spark:3.5.0

WORKDIR /app

# Install netcat-traditional for healthchecks if not already present
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user for Spark (Bitnami images might already have 'spark' user)
RUN groupadd -g 1337 spark && useradd -m -u 1337 -g spark spark

# Copy Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application files (streaming_app.py, model.py, fraud_rules.py)
COPY streaming_app.py model.py fraud_rules.py ./

# CRITICAL FIX: Copy the Neo4j Spark Connector JAR to the /app directory
# This assumes you have downloaded 'neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar'
# into the 'spark_app' directory on your VM.
COPY neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar /app/

# Make the main script executable
RUN chmod +x streaming_app.py