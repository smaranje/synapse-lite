    # ai_service/Dockerfile
    # This Dockerfile builds the image for your Flask LLM service.

    # Use a lightweight Python base image
    FROM python:3.9-slim-buster

    # Set the working directory inside the container
    WORKDIR /app

    # Install system dependencies if any are needed for Python packages
    # For example, if you had packages requiring compilation tools
    # RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

    # Copy the requirements file into the container
    COPY requirements.txt .

    # Install Python dependencies
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy your Flask application code
    COPY app.py .

    # Expose the port your Flask app will run on
    EXPOSE 5000

    # Command to run the Flask application
    CMD ["python", "app.py"]
    