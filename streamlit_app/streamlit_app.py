import streamlit as st
import pandas as pd
import requests
import json
import time
from neo4j import GraphDatabase, basic_auth
import os
import html # Import the html module
from datetime import datetime, timedelta

# Configuration for Flask LLM service
LLM_SERVICE_URL = os.environ.get('LLM_SERVICE_URL', 'http://flask-llm-service:5000')

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
    /* Styles for Transaction Monitor */
    .transaction-card {
        background-color: #2a2a2a;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #444;
    }
    .transaction-card .tx-hash {
        font-weight: bold;
        color: #f0f0f0;
    }
    .transaction-card .tx-from {
        font-size: 0.8rem;
        color: #bbb;
    }
    .transaction-card .tx-amount {
        font-size: 1.1rem;
        font-weight: bold;
        color: #f0f0f0;
    }
    .transaction-card .tx-usd {
        font-size: 0.9rem;
        color: #999;
    }
    .risk-score {
        font-size: 0.9rem;
        padding: 3px 8px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .risk-score.low { background-color: #28a745; color: white; }
    .risk-score.medium { background-color: #17a2b8; color: white; }
    .risk-score.high { background-color: #ffc107; color: #333; }
    .risk-score.critical { background-color: #dc3545; color: white; }
    .transaction-card .tx-status {
        font-size: 0.9rem;
        padding: 3px 8px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .tx-status.confirmed { background-color: #28a745; color: white; }
    .tx-status.pending { background-color: #ffc107; color: #333; }
    .transaction-card .tx-time {
        font-size: 0.9rem;
        color: #bbb;
    }
    /* Styles for Security Alerts section */
    .alert-list-card {
        background-color: #2a2a2a;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #444;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .alert-list-card .alert-content {
        flex-grow: 1;
    }
    .alert-list-card .alert-content h5 {
        margin-top: 0;
        margin-bottom: 5px;
        color: #f0f0f0;
    }
    .alert-list-card .alert-content p {
        font-size: 0.9rem;
        color: #bbb;
        margin-bottom: 5px;
    }
    .alert-list-card .alert-meta {
        font-size: 0.75rem;
        color: #888;
    }
    .alert-list-card .alert-actions {
        margin-left: 15px;
    }
    /* Styles for Analytics section */
    .analytics-card {
        background-color: #2a2a2a;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #444;
        margin-bottom: 20px;
    }
    .analytics-card h4 {
        margin-top: 0;
        color: #f0f0f0;
    }
    .analytics-metric-label {
        color: #bbb;
        font-size: 0.9rem;
    }
    .analytics-metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #f0f0f0;
    }
    .analytics-metric-delta {
        font-size: 0.8rem;
        color: #999;
    }
    .risk-distribution-label {
        font-size: 0.9rem;
        color: #e0e0e0;
    }
    .risk-distribution-value {
        font-size: 1.1rem;
        font-weight: bold;
        color: #f0f0f0;
    }
    .top-risk-address-item {
        background-color: #3a3a3a;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .top-risk-address-item .rank {
        font-weight: bold;
        color: #f0f0f0;
        margin-right: 10px;
    }
    .top-risk-address-item .address-info {
        flex-grow: 1;
    }
    .top-risk-address-item .address-hash {
        font-weight: bold;
        color: #f0f0f0;
    }
    .top-risk-address-item .tx-count {
        font-size: 0.8rem;
        color: #bbb;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Neo4j Connection ---
@st.cache_resource(ttl=300) # Cache the driver for 5 minutes
def get_neo4j_driver():
    """Initializes and returns a Neo4j driver with retry logic."""
    driver = None
    print(f"Attempting to connect to Neo4j for Streamlit at {NEO4J_URI}...")
    for i in range(10): # Retry 10 times
        try:
            driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USERNAME, NEO4J_PASSWORD))
            driver.verify_connectivity()
            st.sidebar.success("Connected to Neo4j successfully!")
            print("Neo4j driver connected for Streamlit.")
            return driver
        except Exception as e:
            st.sidebar.warning(f"Neo4j connection attempt {i+1}/10 failed: {e}. Retrying in 5 seconds...")
            print(f"Streamlit Neo4j connection attempt {i+1}/10 failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    st.sidebar.error("Failed to connect to Neo4j after multiple retries. Graph data will not be available.")
    print("Failed to connect to Neo4j after multiple retries. Graph data will not be available.")
    return None

neo4j_driver = get_neo4j_driver()

# --- Data Fetching Functions from Neo4j ---

@st.cache_data(ttl=5) # Cache for 5 seconds to provide near real-time updates
def fetch_recent_transactions_from_neo4j(limit=10):
    """Fetches recent transactions from Neo4j, regardless of fraud score."""
    if not neo4j_driver:
        return pd.DataFrame() # Return empty DataFrame if no connection
    
    query = f"""
    MATCH (tx:Transaction)
    RETURN tx.hash AS Hash, tx.timestamp AS Timestamp, tx.fee AS Fee, tx.size AS Size,
           tx.vin_sz AS NumInputs, tx.vout_sz AS NumOutputs,
           tx.totalInputValue AS TotalInputValue, tx.totalOutputValue AS TotalOutputValue,
           tx.mlFraudScore AS ML_Score, tx.isSmurfingRule AS Smurfing_Rule
    ORDER BY tx.timestamp DESC
    LIMIT {limit}
    """
    try:
        with neo4j_driver.session() as session:
            result = session.run(query)
            df = pd.DataFrame([r.data() for r in result])
            
            if not df.empty:
                # Convert timestamp to readable format
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
                
                # Calculate BTC values (assuming 1 BTC = 10^8 Satoshis)
                # Need to ensure 'TotalInputValue' and 'TotalOutputValue' are numeric
                df['TotalInputValueBTC'] = df['TotalInputValue'].apply(lambda x: float(x) / 1e8 if x is not None else 0.0)
                df['TotalOutputValueBTC'] = df['TotalOutputValue'].apply(lambda x: float(x) / 1e8 if x is not None else 0.0)

                # Add risk level based on ML_Score or Smurfing_Rule
                df['Risk_Level'] = df.apply(lambda row: get_risk_level(row['ML_Score'], row['Smurfing_Rule']), axis=1)
                
                # Format for display
                df['Amount'] = df.apply(lambda row: f"{row['TotalOutputValueBTC']:.4f} BTC\n${row['TotalOutputValueBTC'] * 65000:,.2f}", axis=1) # Assuming 1 BTC = $65000
                df['Risk'] = df.apply(lambda row: f"{row['Risk_Level']} ({int(row['ML_Score']*100)})" if row['ML_Score'] is not None else row['Risk_Level'], axis=1)
                df['Status'] = 'confirmed' # All transactions in Neo4j are "processed/confirmed" by Spark
                df['Time'] = df['Timestamp'].dt.strftime("%H:%M:%S")
                df['Actions'] = '🔗'
            return df
    except Exception as e:
        st.error(f"Error fetching recent transactions from Neo4j: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=10) # Cache for 10 seconds
def fetch_alerts_from_neo4j(limit=100):
    """Fetches suspicious transactions (alerts) from Neo4j."""
    if not neo4j_driver:
        return pd.DataFrame()

    query = f"""
    MATCH (tx:Transaction)
    WHERE tx.mlFraudScore > 0.5 OR tx.isSmurfingRule = true
    RETURN tx.hash AS Hash, tx.timestamp AS Timestamp, tx.mlFraudScore AS ML_Score,
           tx.isSmurfingRule AS Smurfing_Rule, tx.fee AS Fee, tx.size AS Size,
           tx.feePerByte AS FeePerByte, tx.totalInputValue AS TotalInputValue,
           tx.totalOutputValue AS TotalOutputValue, tx.shapFeaturesJson AS SHAP_Features
    ORDER BY tx.timestamp DESC
    LIMIT {limit}
    """
    try:
        with neo4j_driver.session() as session:
            result = session.run(query)
            df = pd.DataFrame([r.data() for r in result])
            if not df.empty:
                df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
                df['Risk_Level'] = df.apply(lambda row: get_risk_level(row['ML_Score'], row['Smurfing_Rule']), axis=1)
            return df
    except Exception as e:
        st.error(f"Error fetching alerts from Neo4j: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=60) # Cache for 1 minute
def fetch_analytics_data_from_neo4j():
    """Fetches aggregated data for analytics from Neo4j."""
    if not neo4j_driver:
        return {}, pd.DataFrame(), pd.DataFrame(), [], []

    metrics = {
        "total_transactions": 0,
        "active_alerts": 0,
        "critical_alerts": 0,
        "avg_risk_score": 0.0,
        "high_risk_addresses": 0,
        "total_alerts": 0
    }
    
    avg_risk_trends_df = pd.DataFrame()
    high_risk_tx_trends_df = pd.DataFrame()
    risk_distribution_df = pd.DataFrame()
    top_alert_types_list = []
    top_risk_addresses_list = []

    try:
        with neo4j_driver.session() as session:
            # Total Transactions
            total_tx_result = session.run("MATCH (tx:Transaction) RETURN count(tx) AS total_count").single()
            metrics["total_transactions"] = total_tx_result["total_count"] if total_tx_result else 0

            # Total Alerts, Critical Alerts, Active Alerts, Avg Risk Score
            alerts_query = """
            MATCH (tx:Transaction)
            WHERE tx.mlFraudScore IS NOT NULL OR tx.isSmurfingRule = true
            RETURN tx.mlFraudScore AS mlScore, tx.isSmurfingRule AS smurfingRule, tx.timestamp AS timestamp
            """
            alerts_records = session.run(alerts_query).data()
            
            now_ms = time.time() * 1000
            alerts_ml_scores = []
            for record in alerts_records:
                metrics["total_alerts"] += 1
                if record["mlScore"] is not None and record["mlScore"] > 0.9 or record["smurfingRule"]:
                    metrics["critical_alerts"] += 1
                if record["timestamp"] is not None and record["timestamp"] > (now_ms - 24 * 3600 * 1000):
                    metrics["active_alerts"] += 1
                if record["mlScore"] is not None:
                    alerts_ml_scores.append(record["mlScore"])
            
            metrics["avg_risk_score"] = round(sum(alerts_ml_scores) / len(alerts_ml_scores) * 100, 1) if alerts_ml_scores else 0.0

            # Risk Analysis Trends (last 24 hours)
            # Group by hour and calculate average ML score and high-risk count
            trends_query = """
            MATCH (tx:Transaction)
            WHERE tx.timestamp IS NOT NULL AND tx.timestamp > (datetime().epochMillis - 24 * 3600 * 1000)
            RETURN toInteger(tx.timestamp / 3600000) AS hour_bucket,
                   AVG(tx.mlFraudScore) AS avg_ml_score,
                   COUNT(CASE WHEN tx.mlFraudScore > 0.7 OR tx.isSmurfingRule = true THEN tx END) AS high_risk_count
            ORDER BY hour_bucket
            """
            trends_records = session.run(trends_query).data()
            
            avg_risk_data = []
            high_risk_tx_data = []
            for record in trends_records:
                hour_ago = datetime.fromtimestamp(record["hour_bucket"] * 3600)
                hour_label = hour_ago.strftime("%H:00")
                avg_risk_data.append({"Hour": hour_label, "Average Risk Score": record["avg_ml_score"] * 100 if record["avg_ml_score"] is not None else 0.0})
                high_risk_tx_data.append({"Hour": hour_label, "High Risk Transactions": record["high_risk_count"]})
            
            avg_risk_trends_df = pd.DataFrame(avg_risk_data).set_index("Hour").sort_index()
            high_risk_tx_trends_df = pd.DataFrame(high_risk_tx_data).set_index("Hour").sort_index()

            # Risk Score Distribution
            risk_dist_query = """
            MATCH (tx:Transaction)
            WHERE tx.mlFraudScore IS NOT NULL
            RETURN
                SUM(CASE WHEN tx.mlFraudScore < 0.4 THEN 1 ELSE 0 END) AS low,
                SUM(CASE WHEN tx.mlFraudScore >= 0.4 AND tx.mlFraudScore < 0.7 THEN 1 ELSE 0 END) AS medium,
                SUM(CASE WHEN tx.mlFraudScore >= 0.7 AND tx.mlFraudScore < 0.9 THEN 1 ELSE 0 END) AS high,
                SUM(CASE WHEN tx.mlFraudScore >= 0.9 THEN 1 ELSE 0 END) AS critical
            """
            risk_dist_result = session.run(risk_dist_query).single()
            if risk_dist_result:
                total_dist_tx = sum(risk_dist_result.values())
                risk_distribution_data = []
                for category, count in risk_dist_result.items():
                    percentage = (count / total_dist_tx) * 100 if total_dist_tx > 0 else 0.0
                    risk_distribution_data.append({"Category": category.capitalize(), "Transactions": count, "Percentage": f"{percentage:.1f}%"})
                risk_distribution_df = pd.DataFrame(risk_distribution_data)

            # Top Risk Addresses
            top_addresses_query = """
            MATCH (addr:Address)-[:SENT|SENT_TO]-(tx:Transaction)
            WHERE tx.mlFraudScore > 0.7 OR tx.isSmurfingRule = true
            RETURN addr.id AS address, COUNT(DISTINCT tx) AS high_risk_tx_count
            ORDER BY high_risk_tx_count DESC
            LIMIT 5
            """
            top_addresses_records = session.run(top_addresses_query).data()
            top_risk_addresses_list = [
                {"rank": i+1, "address": r["address"], "transactions": r["high_risk_tx_count"], "risk_level": "high"}
                for i, r in enumerate(top_addresses_records)
            ]
            metrics["high_risk_addresses"] = len(top_risk_addresses_list)

            # Top Alert Types (derived from data, not directly stored as types)
            # This is more complex to derive purely from Neo4j without explicit labels/properties for alert types.
            # For now, we can infer from mlFraudScore and isSmurfingRule.
            # If you want more specific types, Spark needs to store them explicitly.
            smurfing_count_query = "MATCH (tx:Transaction) WHERE tx.isSmurfingRule = true RETURN count(tx) AS count"
            high_ml_count_query = "MATCH (tx:Transaction) WHERE tx.mlFraudScore > 0.9 RETURN count(tx) AS count"
            
            smurfing_count = session.run(smurfing_count_query).single()["count"]
            high_ml_count = session.run(high_ml_count_query).single()["count"]

            # Simple placeholder for alert types based on available data
            if smurfing_count > 0:
                top_alert_types_list.append({"type": "Smurfing Rule", "count": smurfing_count, "percentage": f"{(smurfing_count / metrics['total_alerts'])*100:.1f}%" if metrics['total_alerts'] > 0 else "0.0%"})
            if high_ml_count > 0:
                top_alert_types_list.append({"type": "High ML Score", "count": high_ml_count, "percentage": f"{(high_ml_count / metrics['total_alerts'])*100:.1f}%" if metrics['total_alerts'] > 0 else "0.0%"})
            
            # Sort by count descending
            top_alert_types_list.sort(key=lambda x: x['count'], reverse=True)


    except Exception as e:
        st.error(f"Error fetching analytics data from Neo4j: {e}")
        print(f"Error fetching analytics data from Neo4j: {e}")

    return metrics, avg_risk_trends_df, high_risk_tx_trends_df, risk_distribution_df, top_alert_types_list, top_risk_addresses_list


def get_risk_level(ml_score, is_smurfing_rule):
    """Determines risk level based on ML score and smurfing rule."""
    if is_smurfing_rule:
        return "Critical"
    if ml_score is None:
        return "Low" # Default if no ML score
    if ml_score > 0.9:
        return "Critical"
    elif ml_score > 0.7:
        return "High"
    elif ml_score > 0.5:
        return "Medium"
    else:
        return "Low"

# --- LLM Service Interaction ---
def generate_sar_with_llm(alert_data):
    """Calls the Flask LLM service to generate a SAR draft."""
    try:
        response = requests.post(f"{LLM_SERVICE_URL}/generate-sar", json=alert_data, timeout=60) # Increased timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json().get("sar_draft", "No SAR draft generated.")
    except requests.exceptions.ConnectionError:
        st.error(f"LLM Service not reachable at {LLM_SERVICE_URL}. Is the Flask service running?")
        return "LLM Service connection error."
    except requests.exceptions.Timeout:
        st.error("LLM Service timed out. It might be too slow or busy.")
        return "LLM Service timeout."
    except requests.exceptions.RequestException as e:
        st.error(f"Error calling LLM service: {e}")
        return f"LLM Service error: {e}"
    except json.JSONDecodeError:
        st.error(f"Failed to decode JSON from LLM service. Response: {response.text}")
        return "LLM Service response error."

# Sidebar Navigation
with st.sidebar:
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

    # Fetch live analytics metrics
    metrics, _, _, _, _, _ = fetch_analytics_data_from_neo4j()

    with col1:
        st.metric(label="Total Transactions", value=metrics["total_transactions"], delta="All time")
    with col2:
        st.metric(label="Active Alerts (24h)", value=metrics["active_alerts"], delta="Needs attention", delta_color="off")
        st.markdown("<p class='metric-status-orange'>Needs attention</p>", unsafe_allow_html=True)
    with col3:
        st.metric(label="Critical Alerts", value=metrics["critical_alerts"], delta="High priority", delta_color="off")
        st.markdown("<p class='metric-status-red'>High priority</p>", unsafe_allow_html=True)
    with col4:
        st.metric(label="Avg Risk Score", value=f"{metrics['avg_risk_score']:.1f}", delta="0-100 scale")
    with col5:
        st.metric(label="High Risk Addresses", value=metrics["high_risk_addresses"], delta="Under watch", delta_color="off")
        st.markdown("<p class='metric-status-red'>Under watch</p>", unsafe_allow_html=True)
    with col6:
        st.metric(label="Total Alerts (All Time)", value=metrics["total_alerts"], delta="All time")

    st.markdown("---")

    # Live Bitcoin Mempool
    st.subheader("⚡ Live Bitcoin Mempool")
    st.markdown("<p style='color:#28a745; font-weight:bold;'>● Live</p>", unsafe_allow_html=True)
    
    mempool_col1, mempool_col2 = st.columns([0.9, 0.1])
    with mempool_col2:
        if st.button("Refresh", key="mempool_refresh_btn"):
            st.cache_data.clear() # Clear cache for mempool data
            st.rerun()
    
    with mempool_col1:
        with st.spinner("Fetching live mempool data..."):
            live_mempool_df = fetch_recent_transactions_from_neo4j(limit=10)
            if not live_mempool_df.empty:
                # Select and reorder columns for display
                display_cols = ['Hash', 'Amount', 'Risk', 'Status', 'Time', 'Actions']
                st.dataframe(live_mempool_df[display_cols], hide_index=True, use_container_width=True)
            else:
                st.info("No recent transactions available in Neo4j. Waiting for data...")

    st.markdown("---")

    # Active Alerts Section
    st.subheader("🚨 Active Alerts")
    active_alerts_col1, active_alerts_col2, active_alerts_col3 = st.columns([0.1, 0.1, 0.8])
    
    # Fetch alerts for display
    active_alerts_display_df = fetch_alerts_from_neo4j(limit=5) # Limit to top 5 for dashboard
    
    critical_alerts_count_display = len(active_alerts_display_df[active_alerts_display_df['Risk_Level'] == 'Critical'])
    high_alerts_count_display = len(active_alerts_display_df[active_alerts_display_df['Risk_Level'] == 'High'])

    with active_alerts_col1:
        st.markdown(f"<p class='alert-category critical'>{critical_alerts_count_display} Critical</p>", unsafe_allow_html=True)
    with active_alerts_col2:
        st.markdown(f"<p class='alert-category high'>{high_alerts_count_display} Open</p>", unsafe_allow_html=True)
    
    if not active_alerts_display_df.empty:
        for index, alert in active_alerts_display_df.iterrows():
            alert_category = alert['Risk_Level'].lower()
            
            # Example descriptions - these would ideally come from Spark/ML logic
            description = "Unusual transaction pattern detected."
            if alert.get("Smurfing_Rule"):
                description = "Smurfing rule triggered: multiple small outputs."
            elif alert.get("ML_Score", 0) > 0.9:
                description = "High-value transaction with suspicious ML score."
            
            st.markdown(f"""
            <div class="active-alert-card">
                <h5>
                    <span class="alert-category {alert_category}">{alert_category.capitalize()}</span>
                    Alert: {alert['Hash'][:8]}...
                </h5>
                <p>{description}</p>
                <p class="timestamp">{alert['Timestamp'].strftime("%b %d, %H:%M")}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No active alerts found in Neo4j.")
    
    st.button("View All Alerts", key="view_all_alerts_btn") # Button to navigate to full alerts page

    st.markdown("---")

    # Risk Analysis Trends Section
    st.subheader("📈 Risk Analysis Trends")
    st.markdown("---")
    
    _, avg_risk_trends_df, high_risk_tx_trends_df, _, _, _ = fetch_analytics_data_from_neo4j()

    trends_col1, trends_col2 = st.columns(2)

    with trends_col1:
        st.markdown("#### Average Risk Score by Hour")
        if not avg_risk_trends_df.empty:
            st.line_chart(avg_risk_trends_df, use_container_width=True)
        else:
            st.info("No average risk score trend data available.")

    with trends_col2:
        st.markdown("#### High Risk Transactions")
        if not high_risk_tx_trends_df.empty:
            st.line_chart(high_risk_tx_trends_df, use_container_width=True)
        else:
            st.info("No high risk transaction trend data available.")


elif page_selection == "Transactions":
    st.header("Transaction Monitor")
    st.markdown("Real-time Bitcoin transaction analysis and fraud detection")

    # Top row with refresh/export buttons
    top_row_cols = st.columns([0.7, 0.1, 0.1, 0.1])
    with top_row_cols[1]:
        if st.button("Refresh", key="tx_monitor_refresh_btn"):
            st.cache_data.clear() # Clear cache for transaction data
            st.rerun()
    with top_row_cols[2]:
        st.button("Export", key="tx_monitor_export_btn") # Export functionality not implemented

    st.markdown("---")

    # Metrics for Transaction Monitor (using live data)
    tx_metric_cols = st.columns(5)
    
    metrics_tx, _, _, _, _, _ = fetch_analytics_data_from_neo4j() # Re-use analytics metrics

    with tx_metric_cols[0]:
        st.metric(label="Total Transactions", value=metrics_tx["total_transactions"])
    with tx_metric_cols[1]:
        # Live transactions count would be from Kafka consumer, not directly from Neo4j historical data
        st.metric(label="Live (Approx)", value=len(fetch_recent_transactions_from_neo4j(limit=50))) # Count recent ones
    with tx_metric_cols[2]:
        st.metric(label="Flagged (Alerts)", value=metrics_tx["total_alerts"])
    with tx_metric_cols[3]:
        st.metric(label="High Risk (ML/Rule)", value=metrics_tx["critical_alerts"])
    with tx_metric_cols[4]:
        # Sum of output values for all transactions (can be very large)
        # Querying total output value from Neo4j for all transactions might be slow.
        # For simplicity, let's sum recent ones or keep it as a placeholder.
        total_value_query = "MATCH (tx:Transaction) RETURN SUM(tx.totalOutputValue) AS total_value"
        total_value_result = 0
        if neo4j_driver:
            try:
                with neo4j_driver.session() as session:
                    result = session.run(total_value_query).single()
                    total_value_result = result["total_value"] if result and result["total_value"] is not None else 0
            except Exception as e:
                print(f"Error fetching total value: {e}")
        
        st.metric(label="Total Value (BTC)", value=f"{float(total_value_result) / 1e8:.2f}" if total_value_result else "0.00")

    st.markdown("---")

    # Search and Filter Row
    search_filter_cols = st.columns([0.5, 0.15, 0.15, 0.15, 0.05])
    with search_filter_cols[0]:
        transaction_hash_search = st.text_input("Search by hash, address...", key="tx_search_input", label_visibility="collapsed")
    with search_filter_cols[1]:
        tx_status_filter = st.selectbox("All Status", ["All Status", "Confirmed", "Pending"], key="tx_status_filter")
    with search_filter_cols[2]:
        tx_risk_filter = st.selectbox("All Risk", ["All Risk", "Low", "Medium", "High", "Critical"], key="tx_risk_filter")
    with search_filter_cols[3]:
        tx_time_filter = st.selectbox("All Time", ["All Time", "Last Hour", "Last 24h", "Last Week"], key="tx_time_filter")

    st.markdown("---")

    # Transaction Table and Details
    tx_table_col, tx_details_col = st.columns([0.7, 0.3])

    with tx_table_col:
        st.markdown("### Transactions")
        with st.spinner("Fetching transactions..."):
            transactions_df = fetch_recent_transactions_from_neo4j(limit=50) # Fetch more for this view

            # Apply filters if selected
            if transaction_hash_search:
                transactions_df = transactions_df[transactions_df['Hash'].str.contains(transaction_hash_search, case=False, na=False)]
            if tx_status_filter != "All Status":
                # In this demo, all transactions from Neo4j are "confirmed" by Spark processing
                # If you had a 'status' property in Neo4j, you would filter on that.
                pass 
            if tx_risk_filter != "All Risk":
                transactions_df = transactions_df[transactions_df['Risk_Level'] == tx_risk_filter]
            if tx_time_filter != "All Time":
                now = datetime.now()
                if tx_time_filter == "Last Hour":
                    transactions_df = transactions_df[transactions_df['Timestamp'] > (now - timedelta(hours=1))]
                elif tx_time_filter == "Last 24h":
                    transactions_df = transactions_df[transactions_df['Timestamp'] > (now - timedelta(hours=24))]
                elif tx_time_filter == "Last Week":
                    transactions_df = transactions_df[transactions_df['Timestamp'] > (now - timedelta(weeks=1))]

            if not transactions_df.empty:
                # Manually render DataFrame to apply custom styling per row/cell
                st.markdown("""
                <div class="stDataFrame">
                    <table>
                        <thead>
                            <tr>
                                <th>Transaction Hash</th>
                                <th>Amount (BTC)</th>
                                <th>Risk Score</th>
                                <th>Status</th>
                                <th>Time</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                """, unsafe_allow_html=True)
                
                for index, row in transactions_df.iterrows():
                    risk_class = row["Risk_Level"].lower() # Use the Risk_Level for CSS class
                    status_class = row["Status"].lower()
                    
                    st.markdown(f"""
                        <tr>
                            <td>
                                <div class="tx-hash">{html.escape(row["Hash"][:12])}...</div>
                                <div class="tx-from">Inputs: {row['NumInputs']} | Outputs: {row['NumOutputs']}</div>
                            </td>
                            <td>
                                <div class="tx-amount">{html.escape(f"{row['TotalOutputValueBTC']:.4f} BTC")}</div>
                                <div class="tx-usd">{html.escape(f"${row['TotalOutputValueBTC'] * 65000:,.2f}")}</div>
                            </td>
                            <td><span class="risk-score {risk_class}">{html.escape(row["Risk"])}</span></td>
                            <td><span class="tx-status {status_class}">{html.escape(row["Status"])}</span></td>
                            <td><div class="tx-time">{html.escape(row["Timestamp"].strftime("%b %d, %H:%M"))}</div></td>
                            <td><button onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', key: 'selected_tx_hash', value: '{row['Hash']}'}}, '*')" style="background:none; border:none; cursor:pointer; font-size:1.2rem;">🔗</button></td>
                        </tr>
                    """, unsafe_allow_html=True)
                
                st.markdown("""
                        </tbody>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("No transactions found matching your criteria.")

    with tx_details_col:
        st.markdown("### Transaction Details")
        # Use a session state variable to store the selected hash for details
        if 'selected_tx_hash' not in st.session_state:
            st.session_state['selected_tx_hash'] = None

        # This JavaScript snippet captures clicks on the "🔗" button and updates session state
        st.components.v1.html(
            """
            <script>
            window.addEventListener('message', event => {
                if (event.data.type === 'streamlit:setComponentValue' && event.data.key === 'selected_tx_hash') {
                    const hash = event.data.value;
                    window.parent.postMessage(
                        {
                            type: 'streamlit:setComponentValue',
                            args: {
                                key: 'selected_tx_hash',
                                value: hash,
                            },
                        },
                        '*'
                    );
                }
            });
            </script>
            """,
            height=0, width=0
        )

        selected_tx_hash_for_details = st.session_state.selected_tx_hash

        if selected_tx_hash_for_details:
            with st.spinner(f"Fetching details for {selected_tx_hash_for_details[:8]}..."):
                query_tx_details = f"""
                MATCH (tx:Transaction {{hash: '{selected_tx_hash_for_details}'}})
                OPTIONAL MATCH (addr_in:Address)-[s_in:SENT]->(tx)
                OPTIONAL MATCH (tx)-[s_out:SENT_TO]->(addr_out:Address)
                RETURN tx, COLLECT(DISTINCT addr_in.id) AS inputs, COLLECT(DISTINCT addr_out.id) AS outputs
                """
                try:
                    with neo4j_driver.session() as session:
                        result = session.run(query_tx_details).single()

                    if result:
                        tx_node = result["tx"]
                        inputs = result["inputs"]
                        outputs = result["outputs"]

                        st.subheader(f"Transaction: {tx_node['hash'][:12]}...")
                        st.json(tx_node.properties)

                        st.markdown("##### Involved Addresses:")
                        if inputs:
                            st.write(f"**Input Addresses:**")
                            for addr in inputs:
                                st.code(addr)
                        else:
                            st.write("**No Input Addresses found in graph.**")

                        if outputs:
                            st.write(f"**Output Addresses:**")
                            for addr in outputs:
                                st.code(addr)
                        else:
                            st.write("**No Output Addresses found in graph.**")

                        if tx_node.get("shapFeaturesJson"):
                            st.markdown("##### SHAP Feature Contributions:")
                            try:
                                shap_features = json.loads(tx_node["shapFeaturesJson"])
                                for feature, value in shap_features.items():
                                    st.write(f"- **{feature}:** {value:.4f}")
                            except json.JSONDecodeError:
                                st.write("Invalid SHAP features JSON.")
                        else:
                            st.write("No SHAP features available for this transaction.")

                        st.info("For more detailed graph visualization, use the Neo4j Browser at http://<VM_EXTERNAL_IP>:7474")

                    else:
                        st.warning(f"Transaction '{selected_tx_hash_for_details}' not found in the graph database.")
                except Exception as e:
                    st.error(f"Error querying Neo4j for transaction details: {e}")
        else:
            st.markdown("""
            <div style="background-color: #2a2a2a; padding: 20px; border-radius: 10px; border: 1px solid #444; height: 300px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <img src="https://placehold.co/80x80/000/FFF?text=₿" style="border-radius: 50%; margin-bottom: 15px;">
                <p style="text-align: center; color: #bbb;">Select a transaction from the table to view details</p>
            </div>
            """, unsafe_allow_html=True)


elif page_selection == "Alerts":
    st.header("Security Alerts")
    st.markdown("Monitor and investigate suspicious activity and fraud attempts")

    # Top row with refresh button
    alert_top_row_cols = st.columns([0.8, 0.2])
    with alert_top_row_cols[1]:
        if st.button("Refresh", key="alerts_refresh_btn_top"):
            st.cache_data.clear() # Clear cache to refetch data
            st.rerun()
    
    st.markdown("---")

    # Metrics for Security Alerts (using live data)
    alert_metric_cols = st.columns(4)
    
    metrics_alerts, _, _, _, _, _ = fetch_analytics_data_from_neo4j() # Re-use analytics metrics

    with alert_metric_cols[0]:
        st.metric(label="Total Alerts", value=metrics_alerts["total_alerts"])
    with alert_metric_cols[1]:
        st.metric(label="Open (24h)", value=metrics_alerts["active_alerts"])
    with alert_metric_cols[2]:
        st.metric(label="Critical", value=metrics_alerts["critical_alerts"])
    with alert_metric_cols[3]:
        # This metric would need specific tracking of alert statuses (e.g., 'investigating' property in Neo4j)
        st.metric(label="Investigating", value="N/A") # Placeholder for now

    st.markdown("---")

    # Search and Filter Row for Alerts
    alert_search_filter_cols = st.columns([0.4, 0.2, 0.2, 0.2])
    with alert_search_filter_cols[0]:
        alert_hash_search = st.text_input("Search alerts...", key="alert_search_input", label_visibility="collapsed")
    with alert_search_filter_cols[1]:
        alert_status_filter = st.selectbox("All Status", ["All Status", "Open", "Closed", "Investigating"], key="alert_status_filter")
    with alert_search_filter_cols[2]:
        alert_severity_filter = st.selectbox("All Severity", ["All Severity", "Low", "Medium", "High", "Critical"], key="alert_severity_filter")
    with alert_search_filter_cols[3]:
        alert_type_filter = st.selectbox("All Types", ["All Types", "Smurfing Rule", "High ML Score"], key="alert_type_filter")

    st.markdown("---")

    # Alert List and Details
    alert_list_col, alert_details_col = st.columns([0.7, 0.3])

    with alert_list_col:
        st.markdown("### ") # Empty header for alignment
        with st.spinner("Fetching alerts..."):
            alerts_data_df = fetch_alerts_from_neo4j(limit=50) # Fetch more for this view

            # Apply filters
            if alert_hash_search:
                alerts_data_df = alerts_data_df[alerts_data_df['Hash'].str.contains(alert_hash_search, case=False, na=False)]
            if alert_severity_filter != "All Severity":
                alerts_data_df = alerts_data_df[alerts_data_df['Risk_Level'] == alert_severity_filter]
            if alert_type_filter != "All Types":
                if alert_type_filter == "Smurfing Rule":
                    alerts_data_df = alerts_data_df[alerts_data_df['Smurfing_Rule'] == True]
                elif alert_type_filter == "High ML Score":
                    alerts_data_df = alerts_data_df[alerts_data_df['ML_Score'] > 0.9] # Define "High ML Score" threshold

            if not alerts_data_df.empty:
                # Sort by criticality and then timestamp
                alerts_data_df['Sort_Order'] = alerts_data_df['Risk_Level'].map({"Critical": 0, "High": 1, "Medium": 2, "Low": 3})
                alerts_data_df = alerts_data_df.sort_values(by=['Sort_Order', 'Timestamp'], ascending=[True, False])

                for index, alert in alerts_data_df.iterrows():
                    alert_category = alert['Risk_Level'].lower()
                    
                    description = "Unusual transaction pattern detected."
                    if alert.get("Smurfing_Rule"):
                        description = "Smurfing rule triggered: multiple small outputs."
                    elif alert.get("ML_Score", 0) > 0.9:
                        description = "High-value transaction with suspicious ML score."
                    
                    st.markdown(f"""
                    <div class="alert-list-card">
                        <div class="alert-content">
                            <h5>
                                <span class="alert-category {alert_category}">{alert_category.capitalize()}</span>
                                Alert: {html.escape(alert['Hash'][:12])}...
                            </h5>
                            <p>{html.escape(description)}</p>
                            <p class="alert-meta">
                                ML Score: {alert['ML_Score']:.2f} | Smurfing Rule: {alert['Smurfing_Rule']} |
                                Time: {alert['Timestamp'].strftime("%b %d, %H:%M")}
                            </p>
                        </div>
                        <div class="alert-actions">
                            <button onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', key: 'selected_alert_hash', value: '{alert['Hash']}'}}, '*')" style="background-color:#17a2b8; color:white; border-radius:5px; padding:8px 12px; border:none; cursor:pointer;">View Details</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No alerts found matching your criteria.")

    with alert_details_col:
        st.markdown("### Alert Details")
        if 'selected_alert_hash' not in st.session_state:
            st.session_state['selected_alert_hash'] = None

        # This JavaScript snippet captures clicks on the "View Details" button and updates session state
        st.components.v1.html(
            """
            <script>
            window.addEventListener('message', event => {
                if (event.data.type === 'streamlit:setComponentValue' && event.data.key === 'selected_alert_hash') {
                    const hash = event.data.value;
                    window.parent.postMessage(
                        {
                            type: 'streamlit:setComponentValue',
                            args: {
                                key: 'selected_alert_hash',
                                value: hash,
                            },
                        },
                        '*'
                    );
                }
            });
            </script>
            """,
            height=0, width=0
        )

        selected_alert_hash_for_details = st.session_state.selected_alert_hash

        if selected_alert_hash_for_details:
            with st.spinner(f"Fetching alert details for {selected_alert_hash_for_details[:8]}..."):
                query_alert_details = f"""
                MATCH (tx:Transaction {{hash: '{selected_alert_hash_for_details}'}})
                OPTIONAL MATCH (addr_in:Address)-[s_in:SENT]->(tx)
                OPTIONAL MATCH (tx)-[s_out:SENT_TO]->(addr_out:Address)
                RETURN tx, COLLECT(DISTINCT addr_in.id) AS inputs, COLLECT(DISTINCT addr_out.id) AS outputs
                """
                try:
                    with neo4j_driver.session() as session:
                        result = session.run(query_alert_details).single()

                    if result:
                        tx_node = result["tx"]
                        inputs = result["inputs"]
                        outputs = result["outputs"]

                        st.subheader(f"Alert: {tx_node['hash'][:12]}...")
                        st.markdown(f"**ML Fraud Score:** {tx_node.get('mlFraudScore', 'N/A'):.2f}")
                        st.markdown(f"**Smurfing Rule Triggered:** {tx_node.get('isSmurfingRule', 'N/A')}")
                        st.markdown(f"**Transaction Timestamp:** {pd.to_datetime(tx_node.get('timestamp', 0), unit='ms').strftime('%Y-%m-%d %H:%M:%S')}")
                        st.markdown(f"**Total Input Value (BTC):** {float(tx_node.get('totalInputValue', 0)) / 1e8:.4f}")
                        st.markdown(f"**Total Output Value (BTC):** {float(tx_node.get('totalOutputValue', 0)) / 1e8:.4f}")
                        st.markdown(f"**Transaction Fee (BTC):** {float(tx_node.get('fee', 0)) / 1e8:.8f}")
                        st.markdown(f"**Fee Per Byte:** {tx_node.get('feePerByte', 'N/A'):.4f}")

                        st.markdown("##### Involved Addresses:")
                        if inputs:
                            st.write(f"**Input Addresses:**")
                            for addr in inputs:
                                st.code(addr)
                        else:
                            st.write("**No Input Addresses found in graph.**")

                        if outputs:
                            st.write(f"**Output Addresses:**")
                            for addr in outputs:
                                st.code(addr)
                        else:
                            st.write("**No Output Addresses found in graph.**")

                        if tx_node.get("shapFeaturesJson"):
                            st.markdown("##### SHAP Feature Contributions:")
                            try:
                                shap_features = json.loads(tx_node["shapFeaturesJson"])
                                # Sort SHAP features by absolute value for better readability
                                sorted_shap = sorted(shap_features.items(), key=lambda item: abs(item[1]), reverse=True)
                                for feature, value in sorted_shap:
                                    st.write(f"- **{feature}:** {value:.4f}")
                            except json.JSONDecodeError:
                                st.write("Invalid SHAP features JSON.")
                        else:
                            st.write("No SHAP features available for this transaction.")

                        st.markdown("---")
                        st.markdown("##### Generate SAR Draft with LLM:")
                        sar_alert_data = {
                            "transaction_hash": tx_node.get('hash'),
                            "ml_fraud_score": tx_node.get('mlFraudScore'),
                            "is_smurfing_rule": tx_node.get('isSmurfingRule'),
                            "num_inputs": tx_node.get('vin_sz'),
                            "num_outputs": tx_node.get('vout_sz'),
                            "total_input_value": tx_node.get('totalInputValue'),
                            "total_output_value": tx_node.get('totalOutputValue'),
                            "transaction_fee": tx_node.get('fee'),
                            "fee_per_byte": tx_node.get('feePerByte'),
                            "shap_features_json": tx_node.get('shapFeaturesJson', '[]')
                        }
                        if st.button("Generate SAR Draft"):
                            with st.spinner("Generating SAR..."):
                                sar_draft = generate_sar_with_llm(sar_alert_data)
                                st.text_area("SAR Draft", sar_draft, height=300)
                    else:
                        st.warning(f"Alert transaction '{selected_alert_hash_for_details}' not found in the graph database.")
                except Exception as e:
                    st.error(f"Error querying Neo4j for alert details: {e}")
        else:
            st.markdown("""
            <div style="background-color: #2a2a2a; padding: 20px; border-radius: 10px; border: 1px solid #444; height: 300px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <img src="https://placehold.co/80x80/000/FFF?text=🚨" style="border-radius: 50%; margin-bottom: 15px;">
                <p style="text-align: center; color: #bbb;">Select an alert from the list to view details and generate SAR</p>
            </div>
            """, unsafe_allow_html=True)


elif page_selection == "Analytics":
    st.header("Fraud Analytics")
    st.markdown("Deep dive into fraud trends and risk distribution")

    # Top row with refresh button
    analytics_top_row_cols = st.columns([0.8, 0.2])
    with analytics_top_row_cols[1]:
        if st.button("Refresh", key="analytics_refresh_btn_top"):
            st.cache_data.clear() # Clear cache to refetch data
            st.rerun()
    
    st.markdown("---")

    # Fetch analytics data
    metrics_analytics, avg_risk_trends_df, high_risk_tx_trends_df, risk_distribution_df, top_alert_types_list, top_risk_addresses_list = fetch_analytics_data_from_neo4j()

    # Metrics for Analytics
    analytics_metric_cols = st.columns(4)
    with analytics_metric_cols[0]:
        st.metric(label="Total Alerts", value=metrics_analytics["total_alerts"])
    with analytics_metric_cols[1]:
        st.metric(label="Avg Risk Score (All Time)", value=f"{metrics_analytics['avg_risk_score']:.1f}")
    with analytics_metric_cols[2]:
        st.metric(label="Critical Alerts", value=metrics_analytics["critical_alerts"])
    with analytics_metric_cols[3]:
        st.metric(label="High Risk Addresses", value=metrics_analytics["high_risk_addresses"])

    st.markdown("---")

    # Fraud Detection Trends
    st.subheader("Fraud Detection Trends")
    trends_analytics_col1, trends_analytics_col2 = st.columns(2)

    with trends_analytics_col1:
        st.markdown("#### Average Risk Score by Hour (Last 24h)")
        if not avg_risk_trends_df.empty:
            st.line_chart(avg_risk_trends_df, use_container_width=True)
        else:
            st.info("No average risk score trend data available for the last 24 hours.")

    with trends_analytics_col2:
        st.markdown("#### High Risk Transactions (Last 24h)")
        if not high_risk_tx_trends_df.empty:
            st.line_chart(high_risk_tx_trends_df, use_container_width=True)
        else:
            st.info("No high risk transaction trend data available for the last 24 hours.")
    
    st.markdown("---")

    # Risk Score Distribution & Top Alert Types
    risk_dist_col, top_alerts_col = st.columns(2)

    with risk_dist_col:
        st.subheader("Risk Score Distribution")
        if not risk_distribution_df.empty:
            st.dataframe(risk_distribution_df, hide_index=True, use_container_width=True)
        else:
            st.info("No risk distribution data available.")

    with top_alerts_col:
        st.subheader("Top Alert Types")
        if top_alert_types_list:
            for alert_type in top_alert_types_list:
                st.markdown(f"""
                <div class="top-risk-address-item">
                    <div class="address-info">
                        <div class="address-hash">{html.escape(alert_type['type'])}</div>
                        <div class="tx-count">{alert_type['count']} Alerts ({alert_type['percentage']})</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No top alert types data available.")

    st.markdown("---")

    # Top Risk Addresses
    st.subheader("Top Risk Addresses")
    if top_risk_addresses_list:
        for item in top_risk_addresses_list:
            st.markdown(f"""
            <div class="top-risk-address-item">
                <span class="rank">#{item['rank']}</span>
                <div class="address-info">
                    <div class="address-hash">{html.escape(item['address'][:12])}...</div>
                    <div class="tx-count">{item['transactions']} High-Risk Transactions</div>
                </div>
                <span class="risk-score {item['risk_level']}">{item['risk_level'].capitalize()}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No top risk addresses data available.")


elif page_selection == "Settings":
    st.header("Settings")
    st.markdown("Configure application parameters")

    st.subheader("Neo4j Connection Settings")
    st.info(f"Current Neo4j URI: `{NEO4J_URI}`")
    st.info(f"Current Neo4j Username: `{NEO4J_USERNAME}`")
    st.warning("To change Neo4j settings, please modify the `docker-compose.yml` file and rebuild the Streamlit container.")

    st.subheader("LLM Service Settings")
    st.info(f"Current LLM Service URL: `{LLM_SERVICE_URL}`")
    st.warning("To change LLM Service URL, please modify the `docker-compose.yml` file and rebuild the Streamlit container.")

    st.subheader("Data Retention")
    st.write("Data retention policies are managed by your Neo4j and Kafka configurations.")
    st.info("Consider configuring Kafka topic retention and Neo4j database sizing for long-term data storage.")

    st.markdown("---")
    st.write("For advanced configurations, please refer to the project's documentation.")

