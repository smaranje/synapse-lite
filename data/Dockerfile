# data/Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the new Bitcoin mempool consumer script
# CHANGE THIS LINE:
COPY bitcoin_mempool_consumer.py .

# Command is set in docker-compose.yml