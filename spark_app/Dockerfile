# ────────────────────────────────────────────────────────────────
# spark_app/Dockerfile (use for spark-master / spark-worker too)
# ────────────────────────────────────────────────────────────────
FROM bitnami/spark:3.5.6

# ─── build as root ──────────────────────────────────────────────
USER root
WORKDIR /app

# tiny utilities we actually use
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl netcat-traditional \
 && rm -rf /var/lib/apt/lists/*

# Neo4j ⇆ Spark connector
# FIX: Changed to Scala 2.12 connector version 5.3.6_for_spark_3
ARG NEO4J_CONNECTOR_VERSION=5.3.6_for_spark_3
RUN curl -fsSL \
  https://repo1.maven.org/maven2/org/neo4j/neo4j-connector-apache-spark_2.12/${NEO4J_CONNECTOR_VERSION}/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar \
  -o /opt/bitnami/spark/jars/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar

# Kafka client library - ensure it's present if not pulled transitively by spark-sql-kafka
# This is usually pulled by spark-sql-kafka, but explicitly ensuring its presence
# is good practice if you encounter issues. For now, we'll rely on the --packages to pull it.
# If you manually put it here, ensure the version matches what spark-sql-kafka expects.
# RUN curl -fsSL \
#   https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.1/kafka-clients-3.4.1.jar \
#   -o /opt/bitnami/spark/jars/kafka-clients-3.4.1.jar


# Python layer
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# application code
COPY streaming_app.py model.py fraud_rules.py ./
RUN chmod +x streaming_app.py

# ─── create a real spark user ───────────────────────────────────
# Create the spark user and group in a separate RUN command to ensure they are available
RUN groupadd -g 1337 spark \
 && useradd  -u 1337 -g spark -m -d /home/spark spark

# ─── fix ownership for /app, /opt/bitnami/spark/jars, and /opt/bitnami/spark/work ─────────
# Now change ownership of the application directory, Spark JARs directory,
# and the Spark work directory.
# This step runs after the 'spark' user and group are guaranteed to exist.
RUN chown -R spark:spark /app /opt/bitnami/spark/jars /opt/bitnami/spark/work

USER spark
ENV HOME=/home/spark

EXPOSE 8080 4040 7077

# CMD instruction formatted on a single line to prevent parsing errors
# FIX: Updated Kafka connector version in --packages to 3.5.1 (Scala 2.12)
# FIX: Explicitly include the Neo4j connector JAR (now _2.12) in --jars
CMD ["/opt/bitnami/spark/bin/spark-submit", \
    "--master", "spark://spark-master:7077", \
    "--deploy-mode", "client", \
    "--name", "BitcoinFraudDetection", \
    "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1", \
    "--jars", "/opt/bitnami/spark/jars/neo4j-connector-apache-spark_2.12-5.3.6_for_spark_3.jar", \
    "--py-files", "/app/model.py,/app/fraud_rules.py", \
    "/app/streaming_app.py"]
