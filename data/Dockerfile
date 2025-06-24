    # data/Dockerfile
    # Use a Confluent Kafka Tools image as base, which already includes kafka-console-producer
    # This is more robust as it relies on a managed image for Kafka tools
    FROM confluentinc/cp-kafka:7.5.0

    # Install Python on top of the Confluent image using yum (for RHEL/CentOS-based images)
    # Temporarily switch to root to install packages
    USER root
    RUN yum update -y && yum install -y python3 python3-pip \
        && yum clean all \
        && rm -rf /var/cache/yum

    # REMOVED: RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1
    # This command caused the "primary link for python must be /usr/bin/unversioned-python" error
    # because it's not compatible with this specific base image's Python setup.
    # We will explicitly use 'python3' in the docker-compose command.

    WORKDIR /app

    # Install Python dependencies from requirements.txt
    COPY requirements.txt .
    # ********* CRITICAL FIX: Use pip3 instead of pip *********
    RUN pip3 install --no-cache-dir -r requirements.txt

    # Copy the Bitcoin mempool consumer script
    COPY bitcoin_mempool_consumer.py .

    # No need to manually download/extract Kafka tools or set PATH,
    # as the base image already provides them.

    # Switch back to the default user of the base image (usually 'appuser' with UID 1000 for Confluent images)
    USER 1000
