# streamlit_app/streamlit_app.py - Full Stack version with Neo4j integration
import streamlit as st
import pandas as pd
import requests
import json
import time
from cassandra.cluster import Cluster, ResultSet
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory
from neo4j import GraphDatabase, basic_auth
import os

# Configuration for Flask LLM service
LLM_SERVICE_URL = os.environ.get('LLM_SERVICE_URL', 'http://flask-llm-service:5000/generate-sar')

# Cassandra Configuration
CASSANDRA_CONTACT_POINTS = os.environ.get('CASSANDRA_CONTACT_POINTS', 'cassandra').split(',')
CASSANDRA_KEYSPACE = os.environ.get('CASSANDRA_KEYSPACE', 'synapse_lite_ks')
# No explicit username/password for Cassandra in this local setup, it defaults to none
# auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra') # Uncomment if you set up auth

# Neo4j Configuration
NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'password')


st.set_page_config(layout="wide", page_title="Synapse-Lite Fraud Detector")

st.title("🛡️ Synapse-Lite: Real-time Fraud Detection Dashboard")
st.markdown("---")

@st.cache_resource
def get_cassandra_session():
    try:
        # cluster = Cluster(CASSANDRA_CONTACT_POINTS, auth_provider=auth_provider) # Use auth_provider if uncommented
        cluster = Cluster(CASSANDRA_CONTACT_POINTS)
        session = cluster.connect()
        session.set_keyspace(CASSANDRA_KEYSPACE)
        session.row_factory = dict_factory # Return rows as dictionaries
        st.success("Connected to Cassandra successfully!")
        return session
    except Exception as e:
        st.error(f"Failed to connect to Cassandra: {e}. Please ensure Cassandra is running and accessible.")
        return None

@st.cache_resource
def get_neo4j_driver():
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD))
        driver.verify_connectivity()
        st.success("Connected to Neo4j successfully!")
        return driver
    except Exception as e:
        st.error(f"Failed to connect to Neo4j: {e}. Please ensure Neo4j is running and accessible.")
        return None

cassandra_session = get_cassandra_session()
neo4j_driver = get_neo4j_driver()

st.sidebar.header("Navigation")
page_selection = st.sidebar.radio("Go to", ["Live Alerts", "About Synapse-Lite"])

if page_selection == "Live Alerts":
    st.header("Recent Fraud Alerts")

    # Function to fetch alerts from Cassandra
    def fetch_alerts_from_cassandra():
        if cassandra_session:
            try:
                rows: ResultSet = cassandra_session.execute(f"SELECT * FROM alerts LIMIT 100 ALLOW FILTERING;")
                alerts_data = list(rows)
                return alerts_data
            except Exception as e:
                st.error(f"Error fetching alerts from Cassandra: {e}")
                return []
        return []

    # Use a container for alerts to allow for updates
    alerts_container = st.container()

    if st.button("Refresh Alerts"):
        st.cache_data.clear() # Clear cache to refetch data
        st.rerun() # Rerun the app to show updated data

    with alerts_container:
        alerts_data = fetch_alerts_from_cassandra()
        if alerts_data:
            alerts_df = pd.DataFrame(alerts_data)
            
            # Convert timestamps and ensure correct types
            if 'transaction_timestamp' in alerts_df.columns:
                alerts_df["timestamp_readable"] = pd.to_datetime(alerts_df["transaction_timestamp"], unit='ms')
            if 'alert_timestamp_ms' in alerts_df.columns:
                alerts_df["alert_timestamp_readable"] = pd.to_datetime(alerts_df["alert_timestamp_ms"], unit='ms')

            # Filter out alerts without a hash (primary key) if any malformed data sneaks in
            alerts_df = alerts_df.dropna(subset=['transaction_hash'])

            # Sort by alert_timestamp_readable if it exists, otherwise by transaction_hash
            if 'alert_timestamp_readable' in alerts_df.columns:
                alerts_df = alerts_df.sort_values(by="alert_timestamp_readable", ascending=False)
            else:
                st.warning("`alert_timestamp_ms` column not found or not in expected format for sorting.")

            # Display alerts as an interactive table
            display_cols = [
                "alert_timestamp_readable", "transaction_hash", "num_inputs", "num_outputs",
                "total_input_value", "total_output_value", "transaction_fee",
                "fee_per_byte", "ml_fraud_score", "is_smurfing_rule"
            ]
            # Ensure all display_cols actually exist in the DataFrame before selecting
            display_cols_present = [col for col in display_cols if col in alerts_df.columns]

            st.dataframe(alerts_df[display_cols_present].set_index("alert_timestamp_readable"), use_container_width=True)

            st.markdown("---")
            st.subheader("Alert Details and Explanations")

            selected_alert_hash = st.selectbox(
                "Select an Alert to View Details and Generate SAR:",
                alerts_df["transaction_hash"].tolist()
            )

            selected_alert = alerts_df[alerts_df["transaction_hash"] == selected_alert_hash].iloc[0].to_dict()

            if selected_alert:
                st.write(f"**Transaction Hash:** {selected_alert['transaction_hash']}")
                st.write(f"**Size:** {selected_alert.get('size', 'N/A')} bytes")
                st.write(f"**Number of Inputs:** {selected_alert.get('num_inputs', 'N/A')}")
                st.write(f"**Number of Outputs:** {selected_alert.get('num_outputs', 'N/A')}")
                st.write(f"**Total Input Value:** {selected_alert.get('total_input_value', 'N/A')}")
                st.write(f"**Total Output Value:** {selected_alert.get('total_output_value', 'N/A')}")
                st.write(f"**Transaction Fee:** {selected_alert.get('transaction_fee', 'N/A')}")
                st.write(f"**Fee Per Byte:** {selected_alert.get('fee_per_byte', 'N/A'):.4f}" if isinstance(selected_alert.get('fee_per_byte'), (int, float)) else f"**Fee Per Byte:** {selected_alert.get('fee_per_byte', 'N/A')}")
                st.write(f"**ML Fraud Score:** {selected_alert.get('ml_fraud_score', 'N/A'):.2f}" if isinstance(selected_alert.get('ml_fraud_score'), (int, float)) else f"**ML Fraud Score:** {selected_alert.get('ml_fraud_score', 'N/A')}")
                st.write(f"**Smurfing Rule Triggered:** {'Yes' if selected_alert.get('is_smurfing_rule') else 'No'}")
                
                if 'transaction_timestamp' in selected_alert and selected_alert['transaction_timestamp'] is not None:
                    st.write(f"**Transaction Time:** {pd.to_datetime(selected_alert['transaction_timestamp'], unit='ms')}")
                if 'alert_timestamp_ms' in selected_alert and selected_alert['alert_timestamp_ms'] is not None:
                    st.write(f"**Alert Generated At:** {pd.to_datetime(selected_alert['alert_timestamp_ms'], unit='ms')}")

                st.markdown("#### Top Features Driving this Alert (SHAP Insights)")
                shap_features_data = []
                if selected_alert.get('shap_features_json'):
                    try:
                        shap_features_data = json.loads(selected_alert['shap_features_json'])
                    except json.JSONDecodeError:
                        st.error("Error parsing SHAP features JSON.")
                
                shap_data_df = pd.DataFrame(shap_features_data)
                if not shap_data_df.empty:
                    shap_data_df = shap_data_df.sort_values(by="contribution", ascending=True)
                    st.bar_chart(shap_data_df.set_index("name")["contribution"])
                else:
                    st.info("No SHAP features available for this alert or not applicable.")

                st.markdown("#### Graph Visual (Neo4j)")
                if neo4j_driver:
                    with neo4j_driver.session() as session:
                        try:
                            # Fetch related nodes for the selected transaction hash
                            query = """
                            MATCH (tx:Transaction {hash: $transaction_hash})
                            OPTIONAL MATCH (addr_in:Address)-[:SENT]->(tx)
                            OPTIONAL MATCH (tx)-[:SENT_TO]->(addr_out:Address)
                            RETURN tx, COLLECT(addr_in) AS inputAddresses, COLLECT(addr_out) AS outputAddresses
                            """
                            result = session.run(query, transaction_hash=selected_alert_hash).single()
                            if result:
                                tx_node = result["tx"]
                                input_addresses = result["inputAddresses"]
                                output_addresses = result["outputAddresses"]

                                st.write(f"**Central Transaction:** `{tx_node['hash']}`")
                                st.write(f"**Input Addresses ({len(input_addresses)}):**")
                                if input_addresses:
                                    st.code("\n".join([f"- {a['id']}" for a in input_addresses]))
                                else:
                                    st.write("No input addresses found.")

                                st.write(f"**Output Addresses ({len(output_addresses)}):**")
                                if output_addresses:
                                    st.code("\n".join([f"- {a['id']}" for a in output_addresses]))
                                else:
                                    st.write("No output addresses found.")
                                
                                # You could embed a Neo4j Bloom/Browser link here if you wanted
                                st.info(f"Explore this transaction and its connections in the Neo4j Browser at `http://<YOUR_VM_PUBLIC_IP>:7474`")

                            else:
                                st.info("No graph data found for this transaction.")
                        except Exception as e:
                            st.error(f"Error querying Neo4j: {e}")
                else:
                    st.warning("Neo4j driver not connected. Graph visualization will not be available.")

                st.markdown("---")
                st.subheader("AI-Generated SAR Draft")

                if st.button("Generate SAR Draft with LLM"):
                    with st.spinner("Generating SAR draft..."):
                        try:
                            # Prepare alert data for Flask service
                            alert_payload = {
                                "transaction_hash": selected_alert.get('transaction_hash'),
                                "size": selected_alert.get('size'),
                                "transaction_timestamp": selected_alert.get('transaction_timestamp'),
                                "num_inputs": selected_alert.get('num_inputs'),
                                "num_outputs": selected_alert.get('num_outputs'),
                                "total_input_value": selected_alert.get('total_input_value'),
                                "total_output_value": selected_alert.get('total_output_value'),
                                "transaction_fee": selected_alert.get('transaction_fee'),
                                "fee_per_byte": selected_alert.get('fee_per_byte'),
                                "ml_fraud_score": selected_alert.get('ml_fraud_score'),
                                "is_smurfing_rule": selected_alert.get('is_smurfing_rule'),
                                "alert_timestamp_ms": selected_alert.get('alert_timestamp_ms'),
                                "shap_features_json": selected_alert.get('shap_features_json')
                            }
                            # Add input/output addresses to payload for LLM service to potentially use
                            alert_payload['inputAddresses'] = selected_alert.get('inputAddresses', [])
                            alert_payload['outputAddresses'] = selected_alert.get('outputAddresses', [])
                            
                            # Filter out None values from payload
                            alert_payload = {k: v for k, v in alert_payload.items() if v is not None}

                            response = requests.post(LLM_SERVICE_URL, json=alert_payload, timeout=60) # Increased timeout for LLM
                            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                            sar_data = response.json()
                            st.text_area("Draft SAR", sar_data.get("sar_draft", "Error: Could not generate SAR."), height=300)
                        except requests.exceptions.ConnectionError:
                            st.error(f"Error: Could not connect to the Flask LLM service at {LLM_SERVICE_URL}. Is it running?")
                        except requests.exceptions.Timeout:
                            st.error(f"Error: Flask LLM service timed out after 60 seconds. It might be busy or unresponsive.")
                        except requests.exceptions.RequestException as e:
                            st.error(f"An error occurred while calling the LLM service: {e}")
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {e}")
        else:
            st.info("No alerts to display. Data generation or Spark processing might not be active, or there's a database connection issue.")

elif page_selection == "About Synapse-Lite":
    st.header("Project Overview")
    st.markdown("""
    Synapse-Lite is an end-to-end demo application showcasing real-time fraud detection
    using a modern data stack. This full stack deployment highlights:

    * **Real-time Data Streaming (Kafka)**: Ingesting high-volume transaction data.
    * **Distributed Processing (Apache Spark)**: Performing complex analytics,
        feature engineering, and rule-based/ML-driven fraud detection on streams.
    * **NoSQL Database (Cassandra)**: For **persistent storage of real-time alerts**.
    * **Graph Database (Neo4j)**: For **complex relationship analysis** between
        transactions and addresses, visualizing potential fraud networks.
    * **Machine Learning & Explainability (SHAP)**: Scoring transactions for risk
        and explaining *why* a decision was made.
    * **Large Language Models (LLM Integration)**: Automating the drafting of
        Suspicious Activity Reports (SARs) using Google's Gemini API.
    * **Containerization & Orchestration (Docker Compose)**: Packaging and
        deploying the entire stack with a single command.
    * **Interactive Web UI (Streamlit)**: Providing a real-time dashboard for
        monitoring alerts, reviewing SARs, and visualizing graph data.
    """)
    st.subheader("Architecture Diagram (Full Stack)")
    st.markdown("""
    ```mermaid
    graph TD
        A[Data Generator] --> B(Kafka);
        B --> C[Spark Streaming];
        C --> D[Cassandra (Alerts)];
        C --> E[Neo4j (Graph)];
        F[Flask LLM Service] -- Calls Gemini API --> G(Gemini API);
        H[Streamlit Dashboard] --> D;
        H --> E;
        H --> F;
    ```
    """)
    st.markdown("""
    **Conceptual Flow:**
    1.  **Synthetic Data Generator** pushes transactions to **Kafka**.
    2.  **Spark Streaming** consumes from Kafka, performs fraud detection (rules + ML scoring).
    3.  Detected alerts (with ML scores and SHAP insights) are persisted to **Cassandra** and transaction/address relationships are stored in **Neo4j**.
    4.  A **Flask microservice** is ready to generate SAR drafts by calling an LLM (e.g., Gemini API) based on alert details and contextual information.
    5.  The **Streamlit dashboard** pulls real-time alerts from **Cassandra**, queries **Neo4j** for graph visualizations, and allows triggering SAR generation via the **Flask LLM Service**.
    """)