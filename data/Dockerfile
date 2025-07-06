# data/Dockerfile
# This Dockerfile builds the image for your data-generator service.

FROM python:3.9-slim-buster

WORKDIR /app

# Install system dependencies needed for kafka-python (librdkafka-dev is not needed for pure python client)
# If you encounter issues, you might need build-essential and librdkafka-dev, but let's try without first
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     librdkafka-dev \
#     && rm -rf /var/lib/apt/lists/*

# Install Python dependencies, including kafka-python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt kafka-python

# Copy the new Python producer script and the original consumer script
COPY bitcoin_mempool_consumer.py .
COPY producer_app.py .

CMD ["python3", "producer_app.py"]
