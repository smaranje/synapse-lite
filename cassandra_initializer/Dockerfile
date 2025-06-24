    # cassandra_initializer/Dockerfile
    # This Dockerfile is used to create a lightweight image
    # that contains cqlsh for Cassandra schema initialization.

    # Use a Cassandra image as the base, as it already includes cqlsh.
    FROM cassandra:4.1.3

    # Set the working directory inside the container.
    WORKDIR /app

    # Copy the cql_scripts directory from your host into the container.
    # This makes your Cassandra schema definition available inside the container.
    COPY cql_scripts /cql_scripts

    # No specific CMD or ENTRYPOINT is set here, as the command to run
    # the initialization script is defined directly in docker-compose.yml.
    