    # streamlit_app/Dockerfile
    # This Dockerfile builds the image for your Streamlit dashboard.

    # Use a lightweight Python base image
    FROM python:3.9-slim-buster

    # Set the working directory inside the container
    WORKDIR /app

    # Install necessary system dependencies for Streamlit/Python packages
    # For example, if some Python packages have native dependencies
    # RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

    # Copy the requirements file into the container
    COPY requirements.txt .

    # Install Python dependencies
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy your Streamlit application code
    COPY streamlit_app.py .

    # Expose the Streamlit default port
    EXPOSE 8501

    # Command to run the Streamlit application
    # Streamlit runs on 0.0.0.0 to be accessible from outside the container
    CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
    