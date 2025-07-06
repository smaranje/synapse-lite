# streamlit_app/streamlit_app.py - Full Stack version with Neo4j integration (Enhanced Live Dashboard with Risk Trends)
import streamlit as st
import pandas as pd
import requests
import json
import time
from neo4j import GraphDatabase, basic_auth
import os
import random # For mock data generation
from datetime import datetime, timedelta

# Configuration for Flask LLM service
LLM_SERVICE_URL = os.environ.get('LLM_SERVICE_URL', 'http://flask-llm-service:5000/generate-sar')

# Neo4j Configuration
NEO4J_URI = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME', 'neo4j')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD', 'password')


st.set_page_config(layout="wide", page_title="Synapse-Lite Fraud Detector")

# Custom CSS for a darker theme and better aesthetics, mimicking the screenshot
st.markdown("""
    <style>
    .main {
        background-color: #1a1a1a; /* Dark background */
        color: #e0e0e0; /* Light text */
    }
    .stApp {
        background-color: #1a1a1a;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #f0f0f0;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size:1.2rem;
    }
    .stButton>button {
        background-color: #4CAF50; /* Green button */
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stAlert {
        border-radius: 8px;
    }
    .stAlert.stAlert-success {
        background-color: #28a745;
        color: white;
    }
    .stAlert.stAlert-error {
        background-color: #dc3545;
        color: white;
    }
    .stAlert.stAlert-warning {
        background-color: #ffc107;
        color: #333;
    }
    .stAlert.stAlert-info {
        background-color: #17a2b8;
        color: white;
    }
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    /* Metric styling */
    div[data-testid="stMetric"] {
        background-color: #2a2a2a;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #444;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stMetric"] > label {
        color: #bbb;
        font-size: 1rem;
    }
    div[data-testid="stMetric"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 2.5rem;
        font-weight: bold;
        color: #f0f0f0;
    }
    div[data-testid="stMetric"] > div[data-testid="stMarkdownContainer"] > p:last-child {
        font-size: 0.9rem;
        color: #999;
    }
    .metric-status-green { color: #28a745; font-weight: bold; }
    .metric-status-orange { color: #ffc107; font-weight: bold; }
    .metric-status-red { color: #dc3545; font-weight: bold; }

    /* Active Alerts Section */
    .active-alert-card {
        background-color: #2a2a2a;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #444;
    }
    .active-alert-card h5 {
        margin-top: 0;
        margin-bottom: 5px;
        color: #f0f0f0;
    }
    .active-alert-card .alert-category {
        font-size: 0.8rem;
        padding: 3px 8px;
        border-radius: 5px;
        margin-right: 8px;
        font-weight: bold;
    }
    .alert-category.critical { background-color: #dc3545; color: white; }
    .alert-category.high { background-color: #ffc107; color: #333; }
    .alert-category.medium { background-color: #17a2b8; color: white; }
    .alert-category.low { background-color: #28a745; color: white; }
    .active-alert-card p {
        font-size: 0.9rem;
        color: #bbb;
        margin-bottom: 5px;
    }
    .active-alert-card .timestamp {
        font-size: 0.75rem;
        color: #888;
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to generate mock data for Live Bitcoin Mempool
def generate_mock_mempool_data(num_transactions=5):
    data = []
    for _ in range(num_transactions):
        tx_hash = "0x" + ''.join(random.choices('0123456789abcdef', k=random.randint(30, 40)))
        amount_btc = round(random.uniform(0.0001, 10.0), 4)
        amount_usd = round(amount_btc * 65000, 2) # Assuming 1 BTC = $65000
        risk_score = random.randint(1, 100)
        status = random.choice(["confirmed", "pending"])
        time_str = (pd.to_datetime(time.time(), unit='s') - pd.Timedelta(seconds=random.randint(10, 600))).strftime("%H:%M:%S")
        
        risk_level = ""
        if risk_score > 80: risk_level = "High"
        elif risk_score > 50: risk_level = "Medium"
        else: risk_level = "Low"

        data.append({
            "Transaction Hash": tx_hash,
            "Amount": f"{amount_btc:.4f} BTC\n${amount_usd:,.2f}",
            "Risk Score": f"{risk_level} ({risk_score})",
            "Status": status,
            "Time": time_str,
            "Actions": "🔗" # Placeholder for a link/action button
        })
    return pd.DataFrame(data)

# Function to generate mock data for Risk Analysis Trends
def generate_mock_risk_trends_data():
    # Average Risk Score by Hour (last 24 hours)
    avg_risk_data = []
    high_risk_tx_data = []
    now = datetime.now()
    for i in range(24):
        hour_ago = now - timedelta(hours=i)
        hour_label = hour_ago.strftime("%H:00")
        
        # Mock average risk score (e.g., 5-15)
        avg_score = random.uniform(5, 15)
        avg_risk_data.append({"Hour": hour_label, "Average Risk Score": avg_score})

        # Mock high risk transactions count (e.g., 0-5)
        high_risk_count = random.randint(0, 5)
        high_risk_tx_data.append({"Hour": hour_label, "High Risk Transactions": high_risk_count})

    avg_risk_df = pd.DataFrame(avg_risk_data).set_index("Hour").sort_index()
    high_risk_tx_df = pd.DataFrame(high_risk_tx_data).set_index("Hour").sort_index()

    return avg_risk_df, high_risk_tx_df


@st.cache_resource
def get_neo4j_driver():
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD))
        driver.verify_connectivity()
        st.sidebar.success("Connected to Neo4j successfully!")
        return driver
    except Exception as e:
        st.sidebar.error(f"Failed to connect to Neo4j: {e}. Please ensure Neo4j is running and accessible.")
        return None

neo4j_driver = get_neo4j_driver()

# Sidebar Navigation
with st.sidebar:
    # Changed use_column_width to use_container_width
    st.image("https://placehold.co/150x50/000/FFF?text=Synapse-Lite", use_container_width=True) # Placeholder for logo
    st.markdown("## Navigation")
    page_selection = st.radio(
        "Go to",
        ["Dashboard", "Transactions", "Alerts", "Analytics", "Settings"],
        index=0 # Default to Dashboard
    )
    st.markdown("---")
    st.info("Fraud detection@synapse.com") # Placeholder for user info

# --- Main Content Area ---
if page_selection == "Dashboard":
    st.header("Fraud Detection Dashboard")
    st.markdown("Real-time Bitcoin transaction monitoring and threat analysis")

    # Live Monitoring Status
    st.markdown("<p style='color:#28a745; font-weight:bold;'>● Live Monitoring Active</p>", unsafe_allow_html=True)

    # Top Metrics Row
    st.markdown("---")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # Fetch alerts for metrics calculation
    alerts_data_for_metrics = []
    if neo4j_driver:
        try:
            with neo4j_driver.session() as session:
                query_all_alerts = """
                MATCH (tx:Transaction)
                WHERE tx.ml_fraud_score IS NOT NULL AND tx.ml_fraud_score > 0.0
                   OR tx.is_smurfing_rule = true
                RETURN tx
                """
                result_all_alerts = session.run(query_all_alerts)
                for record in result_all_alerts:
                    alerts_data_for_metrics.append(record["tx"])
        except Exception as e:
            st.error(f"Error fetching all alerts for metrics: {e}")

    # Mock/Derived Metrics
    total_transactions = 100 # This would ideally come from a separate transaction count
    active_alerts = len([a for a in alerts_data_for_metrics if a.get("alert_timestamp_ms", 0) > (time.time() * 1000 - 24 * 3600 * 1000)]) # Alerts in last 24h
    critical_alerts = len([a for a in alerts_data_for_metrics if a.get("ml_fraud_score", 0) > 0.9 or a.get("is_smurfing_rule", False)])
    
    avg_risk_scores = [a.get("ml_fraud_score", 0) for a in alerts_data_for_metrics if a.get("ml_fraud_score") is not None]
    avg_risk_score = round(sum(avg_risk_scores) / len(avg_risk_scores) * 100, 1) if avg_risk_scores else 0.0 # Scale to 100
    
    high_risk_addresses = 2 # This would require more complex Neo4j queries for addresses related to critical alerts
    total_alerts = len(alerts_data_for_metrics)

    with col1:
        st.metric(label="Total Transactions", value=total_transactions, delta="24h active")
    with col2:
        st.metric(label="Active Alerts", value=active_alerts, delta="Needs attention", delta_color="off")
        st.markdown("<p class='metric-status-orange'>Needs attention</p>", unsafe_allow_html=True)
    with col3:
        st.metric(label="Critical Alerts", value=critical_alerts, delta="High priority", delta_color="off")
        st.markdown("<p class='metric-status-red'>High priority</p>", unsafe_allow_html=True)
    with col4:
        st.metric(label="Avg Risk Score", value=f"{avg_risk_score:.1f}", delta="0-100 scale")
    with col5:
        st.metric(label="High Risk Addresses", value=high_risk_addresses, delta="Under watch", delta_color="off")
        st.markdown("<p class='metric-status-red'>Under watch</p>", unsafe_allow_html=True)
    with col6:
        st.metric(label="Total Alerts", value=total_alerts, delta="All time")

    st.markdown("---")

    # Live Bitcoin Mempool (Mock Data for now)
    st.subheader("⚡ Live Bitcoin Mempool")
    st.markdown("<p style='color:#28a745; font-weight:bold;'>● Live</p>", unsafe_allow_html=True)
    
    mempool_col1, mempool_col2 = st.columns([0.9, 0.1])
    with mempool_col2:
        if st.button("Refresh", key="mempool_refresh_btn"):
            st.cache_data.clear() # Clear cache for mempool data
            st.rerun()
    
    with mempool_col1:
        st.dataframe(generate_mock_mempool_data(), hide_index=True, use_container_width=True)

    st.markdown("---")

    # Active Alerts Section (Enhanced Display)
    st.subheader("🚨 Active Alerts")
    active_alerts_col1, active_alerts_col2, active_alerts_col3 = st.columns([0.1, 0.1, 0.8])
    with active_alerts_col1:
        st.markdown("<p class='alert-category critical'>2 Critical</p>", unsafe_allow_html=True)
    with active_alerts_col2:
        st.markdown("<p class='alert-category high'>2 Open</p>", unsafe_allow_html=True)
    
    # Filter alerts for display in this section
    active_alerts_display = []
    for alert in alerts_data_for_metrics: # Using the alerts fetched for metrics
        alert_category = "low"
        if alert.get("ml_fraud_score", 0) > 0.9 or alert.get("is_smurfing_rule", False):
            alert_category = "critical"
        elif alert.get("ml_fraud_score", 0) > 0.7:
            alert_category = "high"
        elif alert.get("ml_fraud_score", 0) > 0.5:
            alert_category = "medium"

        # Example descriptions - these would ideally come from Spark/ML logic
        description = "Unusual transaction pattern detected."
        if alert.get("is_smurfing_rule"):
            description = "Smurfing rule triggered: multiple small outputs."
        elif alert.get("ml_fraud_score", 0) > 0.9:
            description = "High-value transaction with suspicious ML score."
        
        active_alerts_display.append({
            "category": alert_category,
            "title": f"Alert: {alert.get('transaction_hash', '')[:8]}...",
            "description": description,
            "timestamp": pd.to_datetime(alert.get("alert_timestamp_ms", time.time()*1000), unit='ms').strftime("%b %d, %H:%M")
        })
    
    # Sort by criticality and then timestamp
    active_alerts_display.sort(key=lambda x: ({"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["category"], 4), x["timestamp"]), reverse=False)

    for alert in active_alerts_display[:5]: # Display top 5 active alerts
        st.markdown(f"""
        <div class="active-alert-card">
            <h5>
                <span class="alert-category {alert['category']}">{alert['category'].capitalize()}</span>
                {alert['title']}
            </h5>
            <p>{alert['description']}</p>
            <p class="timestamp">{alert['timestamp']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.button("View All Alerts", key="view_all_alerts_btn") # Button to navigate to full alerts page

    st.markdown("---")

    # Risk Analysis Trends Section
    st.subheader("📈 Risk Analysis Trends")
    st.markdown("---")
    
    avg_risk_df, high_risk_tx_df = generate_mock_risk_trends_data()

    trends_col1, trends_col2 = st.columns(2)

    with trends_col1:
        st.markdown("#### Average Risk Score by Hour")
        st.line_chart(avg_risk_df, use_container_width=True)

    with trends_col2:
        st.markdown("#### High Risk Transactions")
        st.line_chart(high_risk_tx_df, use_container_width=True)


elif page_selection == "Alerts":
    st.header("Recent Fraud Alerts (Detailed View)")

    # Function to fetch alerts directly from Neo4j
    def fetch_alerts_data_from_neo4j():
        if neo4j_driver:
            try:
                with neo4j_driver.session() as session:
                    # Query Neo4j for Transaction nodes that are flagged as alerts
                    query = """
                    MATCH (tx:Transaction)
                    WHERE tx.ml_fraud_score IS NOT NULL AND tx.ml_fraud_score > 0.0
                       OR tx.is_smurfing_rule = true
                    RETURN tx
                    ORDER BY tx.alert_timestamp_ms DESC
                    LIMIT 100
                    """
                    result = session.run(query)
                    alerts_data = []
                    for record in result:
                        tx_node = record["tx"]
                        # Map Neo4j node properties to the expected alert dictionary format
                        alert_dict = {
                            "transaction_hash": tx_node.get("hash"),
                            "size": tx_node.get("size"),
                            "num_inputs": tx_node.get("num_inputs"),
                            "num_outputs": tx_node.get("num_outputs"),
                            "total_input_value": tx_node.get("total_input_value"),
                            "total_output_value": tx_node.get("total_output_value"),
                            "transaction_fee": tx_node.get("transaction_fee"),
                            "fee_per_byte": tx_node.get("fee_per_byte"),
                            "ml_fraud_score": tx_node.get("ml_fraud_score"),
                            "is_smurfing_rule": tx_node.get("is_smurfing_rule"),
                            "transaction_timestamp": tx_node.get("transaction_timestamp"),
                            "alert_timestamp_ms": tx_node.get("alert_timestamp_ms"),
                            "shap_features_json": tx_node.get("shap_features_json", "[]"), # Ensure it's a string JSON
                            "inputAddresses": [], # Placeholder, fetched in detail view
                            "outputAddresses": [] # Placeholder, fetched in detail view
                        }
                        alerts_data.append(alert_dict)
                    return alerts_data
            except Exception as e:
                st.error(f"Error fetching alerts from Neo4j: {e}. Please ensure Spark is writing alert data to Neo4j Transaction nodes with relevant properties.")
                return []
        else:
            st.warning("Neo4j driver not connected. Cannot fetch live alerts.")
            return []

    # Use a container for alerts to allow for updates
    alerts_container = st.container()

    if st.button("Refresh Alerts", key="detailed_refresh_btn"):
        st.cache_data.clear() # Clear cache to refetch data
        st.rerun() # Rerun the app to show updated data

    with alerts_container:
        alerts_data = fetch_alerts_data_from_neo4j() # Call the Neo4j alert fetching function
        if alerts_data:
            alerts_df = pd.DataFrame(alerts_data)
            
            # Convert timestamps and ensure correct types
            if 'transaction_timestamp' in alerts_df.columns and alerts_df['transaction_timestamp'].dtype == 'int64':
                alerts_df["timestamp_readable"] = pd.to_datetime(alerts_df["transaction_timestamp"], unit='ms')
            else:
                alerts_df["timestamp_readable"] = pd.NaT # Not a Time

            if 'alert_timestamp_ms' in alerts_df.columns and alerts_df['alert_timestamp_ms'].dtype == 'int64':
                alerts_df["alert_timestamp_readable"] = pd.to_datetime(alerts_df["alert_timestamp_ms"], unit='ms')
            else:
                alerts_df["alert_timestamp_readable"] = pd.NaT # Not a Time

            # Filter out alerts without a hash (primary key) if any malformed data sneaks in
            alerts_df = alerts_df.dropna(subset=['transaction_hash'])

            # Sort by alert_timestamp_readable if it exists and is valid, otherwise by transaction_hash
            if 'alert_timestamp_readable' in alerts_df.columns and not alerts_df['alert_timestamp_readable'].isnull().all():
                alerts_df = alerts_df.sort_values(by="alert_timestamp_readable", ascending=False)
            else:
                st.warning("`alert_timestamp_ms` column not found or not in expected format for sorting. Sorting by transaction hash.")
                alerts_df = alerts_df.sort_values(by="transaction_hash", ascending=False) # Fallback sort

            # Display alerts as an interactive table
            display_cols = [
                "alert_timestamp_readable", "transaction_hash", "num_inputs", "num_outputs",
                "total_input_value", "total_output_value", "transaction_fee",
                "fee_per_byte", "ml_fraud_score", "is_smurfing_rule"
            ]
            display_cols_present = [col for col in display_cols if col in alerts_df.columns]

            st.dataframe(alerts_df[display_cols_present].set_index("alert_timestamp_readable"), use_container_width=True)

            st.markdown("---")
            st.subheader("Alert Details and Explanations")

            selected_alert_hash = st.selectbox(
                "Select an Alert to View Details and Generate SAR:",
                alerts_df["transaction_hash"].tolist(),
                key="alert_selectbox"
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
                # Ensure shap_features_json is a string before loading
                if selected_alert.get('shap_features_json') and isinstance(selected_alert['shap_features_json'], str):
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
                            RETURN tx, COLLECT(DISTINCT addr_in) AS inputAddresses, COLLECT(DISTINCT addr_out) AS outputAddresses
                            """
                            result = session.run(query, transaction_hash=selected_alert_hash).single()
                            input_addresses = []
                            output_addresses = []
                            if result:
                                tx_node = result["tx"]
                                input_addresses = [a['id'] for a in result["inputAddresses"]] if result["inputAddresses"] else []
                                output_addresses = [a['id'] for a in result["outputAddresses"]] if result["outputAddresses"] else []

                                st.write(f"**Central Transaction:** `{tx_node['hash']}`")
                                st.write(f"**Input Addresses ({len(input_addresses)}):**")
                                if input_addresses:
                                    st.code("\n".join([f"- {a}" for a in input_addresses]))
                                else:
                                    st.write("No input addresses found.")

                                st.write(f"**Output Addresses ({len(output_addresses)}):**")
                                if output_addresses:
                                    st.code("\n".join([f"- {a}" for a in output_addresses]))
                                else:
                                    st.write("No output addresses found.")
                                
                                # You could embed a Neo4j Bloom/Browser link here if you wanted
                                st.info(f"Explore this transaction and its connections in the Neo4j Browser at `http://<YOUR_VM_PUBLIC_IP>:7474`")

                            else:
                                st.info("No graph data found for this transaction.")
                        except Exception as e:
                            st.error(f"Error querying Neo4j for graph data: {e}")
                else:
                    st.warning("Neo4j driver not connected. Graph visualization will not be available.")

                st.markdown("---")
                st.subheader("AI-Generated SAR Draft")

                if st.button("Generate SAR Draft with LLM", key="generate_sar_btn"):
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
                            alert_payload['inputAddresses'] = input_addresses
                            alert_payload['outputAddresses'] = output_addresses
                            
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
            st.info("No alerts to display. Please ensure Spark is processing data and writing alert-related transaction properties to Neo4j.")

elif page_selection == "Transactions":
    st.header("Transaction Details")
    st.info("This section would display detailed transaction information. (Not implemented in this iteration)")

elif page_selection == "Analytics":
    st.header("Fraud Analytics")
    st.info("This section would provide various analytics and visualizations related to fraud patterns. (Not implemented in this iteration)")

elif page_selection == "Settings":
    st.header("Settings")
    st.info("This section would contain application settings and configurations. (Not implemented in this iteration)")

elif page_selection == "About Synapse-Lite":
    st.header("Project Overview")
    st.markdown("""
    Synapse-Lite is an end-to-end demo application showcasing real-time fraud detection
    using a modern data stack. This full stack deployment highlights:

    * **Real-time Data Streaming (Kafka)**: Ingesting high-volume transaction data.
    * **Distributed Processing (Apache Spark)**: Performing complex analytics,
        feature engineering, and rule-based/ML-driven fraud detection on streams.
    * **Graph Database (Neo4j)**: For **complex relationship analysis** between
        transactions and addresses, visualizing potential fraud networks, and now also
        serving as the **source for live alerts** by storing alert-related properties on transaction nodes.
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
        C --> E[Neo4j (Graph & Alerts)];
        F[Flask LLM Service] -- Calls Gemini API --> G(Gemini API);
        H[Streamlit Dashboard] --> E;
        H --> F;
    ```
    """)
    st.markdown("""
    **Conceptual Flow:**
    1.  **Synthetic Data Generator** pushes transactions to **Kafka**.
    2.  **Spark Streaming** consumes from Kafka, performs fraud detection (rules + ML scoring), and **persists detected alerts (with ML scores and SHAP insights) as properties on Transaction nodes in Neo4j**, along with transaction/address relationships.
    3.  A **Flask microservice** is ready to generate SAR drafts by calling an LLM (e.g., Gemini API) based on alert details and contextual information.
    4.  The **Streamlit dashboard** pulls real-time alerts directly from **Neo4j** by querying for flagged Transaction nodes, visualizes graph data, and allows triggering SAR generation via the **Flask LLM Service**.
    """)