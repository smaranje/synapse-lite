# spark_app/Dockerfile

# 1) Base Spark image (must be a valid tag)
FROM bitnami/spark:3.5.6

USER root
WORKDIR /app

# 2) Install utilities
RUN apt-get update \
 && apt-get install -y --no-install-recommends netcat-traditional curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 3) Fetch the Neo4j Spark connector
ARG NEO4J_CONNECTOR_VERSION=5.3.8_for_spark_3
RUN curl -L \
    https://repo1.maven.org/maven2/org/neo4j/neo4j-connector-apache-spark_2.12/${NEO4J_CONNECTOR_VERSION}/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar \
    -o /opt/bitnami/spark/jars/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar

# 4) Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 5) Application code
COPY streaming_app.py model.py fraud_rules.py ./
RUN chmod +x streaming_app.py

# 6) Fix ownership so Spark can read everything
RUN chown -R spark:spark /app /opt/bitnami/spark/jars

# 7) Switch to non-root spark user
USER spark
ENV HOME=/home/spark \
    JAVA_TOOL_OPTIONS="-Duser.name=spark" \
    SPARK_SUBMIT_OPTIONS="--conf spark.serializer=org.apache.spark.serializer.KryoSerializer"

# 8) Expose Spark UI and master ports
EXPOSE 8080 4040 7077

# 9) Launch your streaming job
CMD ["/opt/bitnami/spark/bin/spark-submit", \
     "--master", "spark://spark-master:7077", \
     "--deploy-mode", "cluster", \
     "--name", "BitcoinFraudDetection", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0", \
     "--jars", "/opt/bitnami/spark/jars/neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar", \
     "--py-files", "model.py,fraud_rules.py", \
     "streaming_app.py"]
