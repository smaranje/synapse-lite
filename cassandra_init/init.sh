#!/bin/bash
# cassandra_init/init.sh

# Wait for Cassandra to be ready
echo "Waiting for Cassandra to start for schema initialization..."
MAX_RETRIES=60 # Try for up to 60 * 5 = 300 seconds (5 minutes)
RETRY_INTERVAL=5 # seconds
COUNT=0

until cqlsh -e "DESCRIBE KEYSPACES" > /dev/null 2>&1; do
  COUNT=$((COUNT + 1))
  if [ $COUNT -ge $MAX_RETRIES ]; then
    echo "Cassandra did not become available for schema init after $MAX_RETRIES attempts. This might indicate a serious issue or prolonged startup. Continuing to start Cassandra."
    # Do NOT exit 1 here, just log and let the main Cassandra process try to start.
    break
  fi
  echo "Cassandra is unavailable for schema init - sleeping for $RETRY_INTERVAL seconds. Attempt $COUNT of $MAX_RETRIES"
  sleep $RETRY_INTERVAL
done

if cqlsh -e "DESCRIBE KEYSPACES" > /dev/null 2>&1; then
  echo "Cassandra is up - executing schema script"
  cqlsh -f /cassandra_init/create_schema.cql
  echo "Cassandra schema initialized successfully."
else
  echo "WARNING: Cassandra not responsive for initial schema creation after attempts. It might start later. Proceeding with Cassandra main process."
fi
# The script will now exit and the main Cassandra command will run.
