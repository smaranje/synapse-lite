# -----------------------------------------------------------------
#  spark_app/Dockerfile  –  upgrade to Spark 3.5.6 + minor hardening
# -----------------------------------------------------------------
    FROM bitnami/spark:3.5.6-debian-12-r0        # ← bumped from 3.5.0

    USER root
    WORKDIR /app
    
    RUN apt-get update \
     && apt-get install -y --no-install-recommends curl netcat-traditional \
     && apt-get clean && rm -rf /var/lib/apt/lists/*
    
    # Spark user
    RUN groupadd -g 1337 spark \
     && useradd -m -u 1337 -g spark spark
    
    # Neo4j connector (same version)
    ARG NEO4J_CONNECTOR_VERSION=5.3.8_for_spark_3
    RUN curl -L \
        https://repo1.maven.org/maven2/org/neo4j/neo4j-connector-apache-spark_2.12/${NEO4J_CONNECTOR_VERSION}/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar \
        -o /opt/bitnami/spark/jars/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar
    
    # Python deps
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    # App code
    COPY streaming_app.py model.py fraud_rules.py ./
    RUN chmod +x streaming_app.py
    RUN chown -R spark:spark /app /opt/bitnami/spark
    
    USER spark
    ENV HOME=/home/spark \
        JAVA_TOOL_OPTIONS="-Duser.name=spark"
    
    # Default to Kryo serializer (defensive)
    ENV SPARK_SUBMIT_OPTIONS="--conf spark.serializer=org.apache.spark.serializer.KryoSerializer"
    
    EXPOSE 8080 4040 7077
    
    CMD ["/opt/bitnami/spark/bin/spark-submit",           \
         "--master",      "spark://spark-master:7077",    \
         "--deploy-mode", "cluster",                      \
         "--name",        "BitcoinFraudDetection",        \
         "--packages",    "org.neo4j:neo4j-connector-apache-spark_2.12:${NEO4J_CONNECTOR_VERSION}", \
         "streaming_app.py"]
    