# spark_app/Dockerfile - Streamlined for Gemini-only
FROM bitnami/spark:3.5.6

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY streaming_app.py .

# Copy the Neo4j Spark Connector JAR
# Ensure this JAR is compatible with Spark 3.5.6 and Scala 2.12
COPY neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar .
