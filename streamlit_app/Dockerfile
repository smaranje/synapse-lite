# streamlit_app/Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY streamlit_app.py /app/streamlit_app.py # THIS IS THE CORRECTED LINE

EXPOSE 8501

CMD ["streamlit", "run", "/app/streamlit_app.py"] # And this is the corresponding CMD
