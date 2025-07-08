# ------------------------------------------------------------
# spark_app/Dockerfile – hardened with Neo4j connector
# ------------------------------------------------------------
    FROM bitnami/spark:3.5.0

    USER root
    WORKDIR /app
    
    # Install curl so we can fetch the Neo4j connector JAR
    RUN apt-get update \
     && apt-get install -y --no-install-recommends netcat-traditional curl \
     && apt-get clean && rm -rf /var/lib/apt/lists/*
    
    # Create spark user
    RUN groupadd -g 1337 spark \
     && useradd -m -u 1337 -g spark spark
    
    # Fetch the Neo4j Spark connector into Spark's jars directory
    ARG NEO4J_CONNECTOR_VERSION=5.3.8_for_spark_3
    RUN curl -L \
      https://repo1.maven.org/maven2/org/neo4j/neo4j-connector-apache-spark_2.12/${NEO4J_CONNECTOR_VERSION}/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar \
      -o /opt/bitnami/spark/jars/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar
    
    # Python dependencies
    COPY requirements.txt .
    RUN pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt
    
    # Application code
    COPY streaming_app.py model.py fraud_rules.py ./
    RUN chmod +x streaming_app.py
    
    # Switch to non-root spark user
    USER spark
    ENV HOME=/home/spark \
        JAVA_TOOL_OPTIONS="-Duser.name=spark"
    
    # Expose Spark ports
    EXPOSE 8080 4040 7077
    
    # Launch the streaming job via spark-submit in cluster mode
    CMD ["/opt/bitnami/spark/bin/spark-submit", \
         "--master", "spark://spark-master:7077", \
         "--deploy-mode", "cluster", \
         "--name", "BitcoinFraudDetection", \
         "--packages", "org.neo4j:neo4j-connector-apache-spark_2.12:${NEO4J_CONNECTOR_VERSION}", \
         "streaming_app.py"]
    