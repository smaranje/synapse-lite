# data/Dockerfile
# This Dockerfile builds the image for your data-generator service.

FROM python:3.9-slim-buster

WORKDIR /app

# Install Python dependencies, including kafka-python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt kafka-python

# Copy the new Python producer script and the original consumer script
COPY bitcoin_mempool_consumer.py .
COPY producer_app.py .

# The CMD is now handled by docker-compose.yml's command/entrypoint override
# CMD ["python3", "producer_app.py"]
