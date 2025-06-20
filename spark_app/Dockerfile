# spark_app/Dockerfile
# This Dockerfile builds the image for your Spark application.
# It installs Python dependencies and copies your Spark code into the container.

# Use a base image that already has Spark installed (e.g., Bitnami Spark)
FROM bitnami/spark:3.5.0

USER root

# Install netcat for health checks
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Upgrade pip and install Python dependencies.
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy your Python application scripts
COPY streaming_app.py .
COPY model.py .
COPY fraud_rules.py .

EXPOSE 8080

USER 1001

# FINAL FIX HERE: CMD in shell form, explicitly calling bash -c
CMD bash -c "/opt/bitnami/spark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 --master spark://spark-master:7077 --deploy-mode client streaming_app.py"
