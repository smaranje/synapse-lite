# ------------------------------------------------------------
# spark_app/Dockerfile – hardened
# ------------------------------------------------------------
    FROM bitnami/spark:3.5.0

    # ---- system layer ----------------------------------------------------------
    USER root
    WORKDIR /app
    
    RUN apt-get update \
     && apt-get install -y --no-install-recommends netcat-traditional \
     && apt-get clean && rm -rf /var/lib/apt/lists/*
    
    RUN groupadd -g 1337 spark \
     && useradd -m -u 1337 -g spark spark
    
    # ---- python deps -----------------------------------------------------------
    COPY requirements.txt .
    RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
    
    # ---- application code ------------------------------------------------------
    COPY streaming_app.py model.py fraud_rules.py ./
    RUN chmod +x streaming_app.py
    
    # ---- runtime user & sane env ----------------------------------------------
    USER spark
    ENV HOME=/home/spark \
        JAVA_TOOL_OPTIONS="-Duser.name=spark"
    
    # ---- open useful ports & fallback shell ------------------------------------
    EXPOSE 8080 4040 7077
    CMD ["/opt/bitnami/spark/bin/spark-shell"]
    