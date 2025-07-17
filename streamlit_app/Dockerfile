# streamlit_app/Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all necessary files
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py"]
