    -- cassandra_initializer/cql_scripts/init.cql

    -- Create the keyspace if it doesn't already exist.
    -- replication_factor = 1 is suitable for a single-node Cassandra setup in a demo.
    CREATE KEYSPACE IF NOT EXISTS synapse_lite_ks WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

    -- Use the newly created or existing keyspace for subsequent commands.
    USE synapse_lite_ks;

    -- Create the alerts table to store fraud alerts detected by Spark.
    -- This schema should match the data structure Spark will write to Cassandra.
    CREATE TABLE IF NOT EXISTS alerts (
        transaction_hash TEXT PRIMARY KEY,
        size INT,
        transaction_timestamp BIGINT,
        num_inputs INT,
        num_outputs INT,
        total_input_value BIGINT,
        total_output_value BIGINT,
        transaction_fee BIGINT,
        fee_per_byte DOUBLE,
        ml_fraud_score DOUBLE,
        is_smurfing_rule BOOLEAN,
        alert_timestamp_ms BIGINT,
        shap_features_json TEXT
    );
    