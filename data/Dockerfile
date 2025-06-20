# data/Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY synthetic_transactions.py .

CMD ["python", "synthetic_transactions.py"]