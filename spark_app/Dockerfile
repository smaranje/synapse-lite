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

# Neo4j ⇆ Spark connector (exact same version the job expects)
# FIX: Corrected typo from NEO44J_CONNECTOR_VERSION to NEO4J_CONNECTOR_VERSION
ARG NEO4J_CONNECTOR_VERSION=5.3.8_for_spark_3
RUN curl -fsSL \
  https://repo1.maven.org/maven2/org/neo4j/neo4j-connector-apache-spark_2.12/${NEO4J_CONNECTOR_VERSION}/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar \
  -o /opt/bitnami/spark/jars/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar

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
CMD ["/opt/bitnami/spark/bin/spark-submit", "--master", "spark://spark-master:7077", "--deploy-mode", "client", "--name", "BitcoinFraudDetection", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0", "--jars", "/opt/bitnami/spark/jars/neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar", "--py-files", "/app/model.py,/app/fraud_rules.py", "/app/streaming_app.py"]
