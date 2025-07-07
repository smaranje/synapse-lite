# -------------------------------------------------
# Builds the Spark + app image
# -------------------------------------------------
    FROM bitnami/spark:3.5.0

    USER root
    WORKDIR /app
    
    # Utilities (netcat for health-checks)
    RUN apt-get update && \
        apt-get install -y netcat-traditional && \
        rm -rf /var/lib/apt/lists/*
    
    # Python deps
    COPY requirements.txt .
    RUN pip install --upgrade pip && \
        pip install --no-cache-dir -r requirements.txt
    
    # Application code
    COPY streaming_app.py .
    COPY model.py .
    COPY fraud_rules.py .
    
    # Make the main script executable (helps when you run it directly)
    RUN chmod +x streaming_app.py
    
    # Expose Spark master UI just in case container is used standalone
    EXPOSE 8080
    
    # Drop privileges to the unprivileged spark user bundled by Bitnami
    USER 1001
    
    # Fallback interactive shell (compose overrides this with spark-submit)
    CMD ["/opt/bitnami/spark/bin/spark-shell"]