# streamlit_app/streamlit_app.py
import streamlit as st
import pandas as pd
import requests
import json
import time

# Configuration for Flask LLM service
# 'flask-llm-service' is the service name in docker-compose.yml
FLASK_LLM_SERVICE_URL = "http://flask-llm-service:5000/generate-sar"

st.set_page_config(layout="wide", page_title="Synapse-Lite Fraud Detector")

st.title("🛡️ Synapse-Lite: Real-time Fraud Detection Dashboard")
st.markdown("---")

# --- Dummy Alerts (For Initial Demo without full DB integration) ---
# In a real scenario, this would fetch from Cassandra in real-time.
dummy_alerts = [
    {
        "transaction_id": "tx_abc_123",
        "sender_account": "ACC_XYZ_001",
        "receiver_account": "ACC_SMURF_005",
        "amount": 55.75,
        "timestamp": int(time.time() * 1000) - 120000, # 2 mins ago
        "ml_fraud_score": 0.92,
        "is_smurfing_rule": True,
        "alert_timestamp": int(time.time() * 1000) - 110000,
        "shap_features_json": '[{"feature": "LowAmount", "value": 55.75, "contribution": 0.4}, {"feature": "SmurfPatternDetected", "value": true, "contribution": 0.3}, {"feature": "AccountActivity", "value": "Frequent", "contribution": 0.2}]'
    },
    {
        "transaction_id": "tx_def_456",
        "sender_account": "ACC_NORM_123",
        "receiver_account": "ACC_NORM_456",
        "amount": 8750.00,
        "timestamp": int(time.time() * 1000) - 60000, # 1 min ago
        "ml_fraud_score": 0.85,
        "is_smurfing_rule": False,
        "alert_timestamp": int(time.time() * 1000) - 50000,
        "shap_features_json": '[{"feature": "HighMLScore", "value": 0.85, "contribution": 0.5}, {"feature": "TransactionFrequency", "value": "Daily", "contribution": 0.3}]'
    },
    {
        "transaction_id": "tx_ghi_789",
        "sender_account": "ACC_SMURF_002",
        "receiver_account": "ACC_SMURF_008",
        "amount": 99.99,
        "timestamp": int(time.time() * 1000) - 30000, # 30 secs ago
        "ml_fraud_score": 0.78, # Slightly lower ML score, but smurfing rule
        "is_smurfing_rule": True,
        "alert_timestamp": int(time.time() * 1000) - 20000,
        "shap_features_json": '[{"feature": "SmurfPatternDetected", "value": true, "contribution": 0.6}, {"feature": "LowAmount", "value": 99.99, "contribution": 0.3}]'
    }
]

# Convert shap_features_json string to actual list of dicts
for alert in dummy_alerts:
    if "shap_features_json" in alert and isinstance(alert["shap_features_json"], str):
        alert["shap_features"] = json.loads(alert["shap_features_json"])
    else:
        alert["shap_features"] = []


st.sidebar.header("Navigation")
page_selection = st.sidebar.radio("Go to", ["Live Alerts", "About Synapse-Lite"])

if page_selection == "Live Alerts":
    st.header("Recent Fraud Alerts (Simulated Live Feed)")

    # Use a container for alerts to allow for updates
    alerts_container = st.container()

    # Simulate real-time updates by re-running a section
    if st.button("Refresh Alerts (Simulated)"):
        # In a real app, this would query Cassandra for new data
        pass

    with alerts_container:
        if dummy_alerts:
            alerts_df = pd.DataFrame(dummy_alerts)
            alerts_df["timestamp_readable"] = pd.to_datetime(alerts_df["timestamp"], unit='ms')
            alerts_df["alert_timestamp_readable"] = pd.to_datetime(alerts_df["alert_timestamp"], unit='ms')

            # Display alerts as an interactive table
            st.dataframe(alerts_df[[
                "alert_timestamp_readable", "transaction_id", "sender_account",
                "receiver_account", "amount", "ml_fraud_score", "is_smurfing_rule"
            ]].sort_values(by="alert_timestamp_readable", ascending=False).set_index("alert_timestamp_readable"), use_container_width=True)

            st.markdown("---")
            st.subheader("Alert Details and Explanations")

            selected_alert_id = st.selectbox(
                "Select an Alert to View Details and Generate SAR:",
                alerts_df["transaction_id"].tolist()
            )

            selected_alert = alerts_df[alerts_df["transaction_id"] == selected_alert_id].iloc[0].to_dict()

            if selected_alert:
                st.write(f"**Transaction ID:** {selected_alert['transaction_id']}")
                st.write(f"**Sender:** {selected_alert['sender_account']} **-> Receiver:** {selected_alert['receiver_account']}")
                st.write(f"**Amount:** ${selected_alert['amount']:.2f}")
                st.write(f"**ML Fraud Score:** {selected_alert['ml_fraud_score']:.2f}")
                st.write(f"**Smurfing Rule Triggered:** {'Yes' if selected_alert['is_smurfing_rule'] else 'No'}")
                st.write(f"**Transaction Time:** {pd.to_datetime(selected_alert['timestamp'], unit='ms')}")
                st.write(f"**Alert Generated At:** {pd.to_datetime(selected_alert['alert_timestamp'], unit='ms')}")

                st.markdown("#### Top Features Driving this Alert (SHAP Insights)")
                shap_data = pd.DataFrame(selected_alert.get('shap_features', []))
                if not shap_data.empty:
                    # Sort by contribution for the bar chart
                    shap_data = shap_data.sort_values(by="contribution", ascending=True)
                    st.bar_chart(shap_data.set_index("feature")["contribution"])
                else:
                    st.info("No SHAP features available for this alert or not applicable.")

                st.markdown("#### Graph Visual (Simulated Placeholder)")
                st.write("*(In a real implementation, this would show a Neo4j visualization of connected accounts in the smurfing cluster.)*")
                # Placeholder for a simple image if you want to add one:
                # st.image("https://placehold.co/400x200/cccccc/000000?text=Neo4j+Graph+View", caption="Simulated Graph Visual")

                st.markdown("---")
                st.subheader("AI-Generated SAR Draft")

                if st.button("Generate SAR Draft with LLM"):
                    with st.spinner("Generating SAR draft..."):
                        try:
                            # Prepare alert data for Flask service
                            alert_payload = {
                                "transaction_id": selected_alert['transaction_id'],
                                "sender_account": selected_alert['sender_account'],
                                "receiver_account": selected_alert['receiver_account'],
                                "amount": selected_alert['amount'],
                                "ml_fraud_score": selected_alert['ml_fraud_score'],
                                "is_smurfing_rule": selected_alert['is_smurfing_rule'],
                                "alert_timestamp": selected_alert['alert_timestamp'],
                                "shap_features": selected_alert.get('shap_features', []) # Pass SHAP data
                            }
                            response = requests.post(FLASK_LLM_SERVICE_URL, json=alert_payload, timeout=10)
                            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                            sar_data = response.json()
                            st.text_area("Draft SAR", sar_data.get("sar_draft", "Error: Could not generate SAR."), height=300)
                        except requests.exceptions.ConnectionError:
                            st.error(f"Error: Could not connect to the Flask LLM service at {FLASK_LLM_SERVICE_URL}. Is it running?")
                        except requests.exceptions.Timeout:
                            st.error("Error: Flask LLM service timed out. It might be busy or unresponsive.")
                        except requests.exceptions.RequestException as e:
                            st.error(f"An error occurred while calling the LLM service: {e}")
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {e}")
        else:
            st.info("No alerts to display. Data generation or Spark processing might not be active.")

elif page_selection == "About Synapse-Lite":
    st.header("Project Overview")
    st.markdown("""
    Synapse-Lite is an end-to-end demo application showcasing real-time fraud detection
    using a modern data stack. It's designed to highlight skills in:

    * **Real-time Data Streaming (Kafka)**: Ingesting high-volume transaction data.
    * **Distributed Processing (Apache Spark)**: Performing complex analytics,
        feature engineering, and rule-based/ML-driven fraud detection on streams.
    * **Graph Databases (Neo4j - _Future Integration_ )**: Detecting complex
        relationship-based fraud patterns like "smurfing".
    * **Machine Learning & Explainability (SHAP)**: Scoring transactions for risk
        and explaining *why* a decision was made.
    * **Large Language Models (LLM Integration)**: Automating the drafting of
        Suspicious Activity Reports (SARs).
    * **Containerization & Orchestration (Docker Compose)**: Packaging and
        deploying the entire stack with a single command.
    * **Interactive Web UI (Streamlit)**: Providing a real-time dashboard for
        monitoring alerts and reviewing SARs.

    This project aims to be a fully reproducible and demonstrable asset for
    showcasing advanced data and AI engineering capabilities.
    """)
    st.subheader("Architecture Diagram (Conceptual)")
    st.write("*(Imagine a clean diagram here: Kafka -> Spark -> Neo4j/Cassandra -> Flask (LLM) -> Streamlit)*")
    st.markdown("""
    **Conceptual Flow:**
    1.  **Synthetic Data Generator** pushes transactions to **Kafka**.
    2.  **Spark Streaming** consumes from Kafka, performs fraud detection (rules + ML scoring).
    3.  Detected alerts (with ML scores and SHAP insights) are persisted to a database (e.g., Cassandra).
    4.  A **Flask microservice** (LLM stub) is ready to generate SAR drafts based on alert details.
    5.  The **Streamlit dashboard** pulls alerts from the database, displays them, visualizes SHAP scores, and allows triggering SAR generation.
    """)