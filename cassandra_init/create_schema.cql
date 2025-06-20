-- cassandra_init/create_schema.cql
CREATE KEYSPACE IF NOT EXISTS synapse_lite_ks WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE synapse_lite_ks;

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