FROM bitnami/spark:3.5.6

WORKDIR /app

# Switch to root user to perform privileged operations
USER root

# Fix APT environment and install packages
RUN mkdir -p /var/lib/apt/lists/partial && \
    apt-get update && \
    apt-get install -y --no-install-recommends netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# Explicitly create the spark user and group if they don't exist
RUN if ! getent group spark; then groupadd -g 1001 spark; fi && \
    if ! getent passwd spark; then useradd -m -u 1001 -g spark spark; fi

# Install Python dependencies as root
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application files with correct ownership
COPY --chown=spark:spark streaming_app.py model.py fraud_rules.py /app/
COPY --chown=spark:spark neo4j-connector-apache-spark_2.12-5.3.8_for_spark_3.jar /app/

# Make the main script executable
RUN chmod +x /app/streaming_app.py

# Switch to the spark user for running the application
USER spark