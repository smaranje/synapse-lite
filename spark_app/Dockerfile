# spark_app/Dockerfile
# This Dockerfile builds the image for your Spark application.
# It installs Python dependencies and copies your Spark code into the container.

# Use a base image that already has Spark installed (e.g., Bitnami Spark)
FROM bitnami/spark:3.5.0

USER root

WORKDIR /app

# Install netcat for health checks and other utilities
# Bitnami images are typically Debian-based, so apt-get is appropriate.
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file
COPY requirements.txt .

# Upgrade pip and install Python dependencies.
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy your Python application scripts
COPY streaming_app.py .
COPY model.py .
COPY fraud_rules.py .

# ********* CRITICAL FIX: Add execute permission to the main script *********
RUN chmod +x streaming_app.py

EXPOSE 8080

USER 1001

# The actual command to run the Spark application is defined in docker-compose.yml
# This CMD is a fallback if no command is specified in docker-compose.yml
CMD ["/opt/bitnami/spark/bin/spark-shell"]