# spark_app/Dockerfile
FROM bitnami/spark:3.5.6

WORKDIR /app

# Copy your Python application files
COPY streaming_app.py .
COPY model.py .
COPY fraud_rules.py .
COPY bitcoin_fraud_model.pkl .

# Copy the Neo4j Spark Connector JAR
# Ensure this JAR is compatible with Spark 3.5.6 and Scala 2.12
COPY neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar .

# Install Python dependencies
RUN pip install pyspark pandas scikit-learn numpy requests neo4j