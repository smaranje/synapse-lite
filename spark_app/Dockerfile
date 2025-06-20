# spark_app/Dockerfile
# This Dockerfile builds the image for your Spark application.
# It installs Python dependencies and copies your Spark code into the container.

# Use a base image that already has Spark installed (e.g., Bitnami Spark)
# This prevents needing to install Spark manually in the Dockerfile.
FROM bitnami/spark:3.5.0

# Temporarily switch to root user to install system-level dependencies (if any)
# and Python packages. Bitnami images usually handle user management well,
# but 'root' ensures permissions for 'pip install'.
USER root

# Set the working directory inside the container.
# All subsequent commands (like COPY, RUN) will be relative to this directory.
WORKDIR /app

# Copy the requirements.txt file from your host machine's spark_app/ directory
# to the /app directory inside the container.
# The path 'requirements.txt' is correct because the build context for this service
# is already set to './spark_app' in your docker-compose.yml.
COPY requirements.txt .

# Upgrade pip to ensure you're using a recent version, then install Python dependencies.
# '--no-cache-dir' reduces the size of the final image by not storing pip's cache.
# '-r requirements.txt' tells pip to install packages listed in the requirements file.
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy your Python application scripts from your host machine's spark_app/ directory
# to the /app directory inside the container.
# Again, these paths are relative to the build context './spark_app'.
COPY streaming_app.py .
COPY model.py .
COPY fraud_rules.py .

# Expose the port typically used for the Spark UI.
# While Spark Master might be on 8080, workers also communicate on certain ports.
# This makes the Spark UI (if running a master locally) accessible from the host.
EXPOSE 8080

# Switch back to a non-root user (recommended security practice)
# User 1001 is a common default for many Docker images or a specific user created by Bitnami.
USER 1001

# Define the default command to run when a container from this image starts.
# For Spark, this typically involves 'spark-submit' to launch your application.
# '--master spark://spark-master:7077' connects to the Spark master service defined in docker-compose.
# '/app/streaming_app.py' is the path to your main Spark application script inside the container.
CMD ["/opt/bitnami/spark/bin/spark-submit", "--master", "spark://spark-master:7077", "/app/streaming_app.py"]
