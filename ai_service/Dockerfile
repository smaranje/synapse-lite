# ai_service/Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

# Corrected COPY commands: Paths are relative to the build context (./ai_service/)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]