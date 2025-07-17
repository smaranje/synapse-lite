FROM bitnami/spark:3.5.6-debian-12-r0

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY streaming_app.py .
COPY fraud_rules.py .
COPY neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar .

CMD ["spark-submit",
     "--master","spark://spark-master:7077",
     "--packages","org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.6",
     "--jars","/app/neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar",
     "/app/streaming_app.py"]
