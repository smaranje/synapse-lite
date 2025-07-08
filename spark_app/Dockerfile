FROM bitnami/spark:3.5.0

############################
# ---- system layer -------
############################
USER root
WORKDIR /app

# curl is needed to fetch the Neo4j connector; netcat is handy for debug
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl netcat-traditional \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

############################
# ---- users / perms ------
############################
# create a dedicated spark user with a well-known UID/GID
ENV SPARK_UID=1337 \
    SPARK_GID=1337
RUN groupadd -g ${SPARK_GID} spark \
 && useradd  -m -u ${SPARK_UID} -g spark spark

# give the non-root user full control of Spark’s work dirs
RUN chown -R spark:spark /opt/bitnami/spark

############################
# ---- neo4j connector ----
############################
ARG NEO4J_CONNECTOR_VERSION=5.3.8_for_spark_3
RUN curl -L \
      https://repo1.maven.org/maven2/org/neo4j/neo4j-connector-apache-spark_2.12/${NEO4J_CONNECTOR_VERSION}/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar \
      -o /opt/bitnami/spark/jars/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar \
 && chown spark:spark /opt/bitnami/spark/jars/neo4j-connector-apache-spark_2.12-${NEO4J_CONNECTOR_VERSION}.jar

############################
# ---- python deps --------
############################
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

############################
# ---- application code ---
############################
COPY streaming_app.py model.py fraud_rules.py ./
RUN chmod +x streaming_app.py \
 && chown -R spark:spark /app

############################
# ---- runtime tweaks -----
############################
USER spark
ENV HOME=/home/spark \
    JAVA_TOOL_OPTIONS="-Duser.name=spark"

EXPOSE 8080 4040 7077

# default command – overridden by docker-compose for master/worker/app roles
CMD ["/bin/bash"]