# streamlit_app/Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

# Corrected COPY commands: Paths are relative to the build context (./streamlit_app/)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
