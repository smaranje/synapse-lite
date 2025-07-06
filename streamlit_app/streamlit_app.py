# streamlit_app/streamlit_app.py - Full Stack version with Neo4j integration (Enhanced Live Dashboard with Analytics Section)
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
    .transaction-card .risk-score {
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

# Function to generate mock data for Transaction Monitor
def generate_mock_transaction_data(num_transactions=10):
    transactions = []
    for _ in range(num_transactions):
        tx_hash = ''.join(random.choices('0123456789abcdef', k=random.randint(20, 30)))
        from_address = ''.join(random.choices('0123456789abcdef', k=random.randint(30, 40)))
        amount_btc = round(random.uniform(0.0001, 50.0), 4)
        amount_usd = round(amount_btc * 65000, 2)
        risk_score_val = random.randint(1, 100)
        risk_level = ""
        if risk_score_val > 80: risk_level = "critical"
        elif risk_score_val > 50: risk_level = "high"
        elif risk_score_val > 20: risk_level = "medium"
        else: risk_level = "low"
        
        status = random.choice(["confirmed", "pending"])
        tx_time = (datetime.now() - timedelta(minutes=random.randint(1, 60))).strftime("%b %d, %H:%M")

        transactions.append({
            "Transaction": f"{tx_hash[:8]}...\nFrom: {from_address[:8]}...",
            "Amount": f"{amount_btc:.4f} BTC\n${amount_usd:,.2f}",
            "Risk": f"{risk_score_val}", # Just the score for the table
            "Risk_Level": risk_level, # For styling
            "Status": status,
            "Time": tx_time,
            "Actions": "🔗" # Placeholder for link/details
        })
    return pd.DataFrame(transactions)

# Function to generate mock data for Fraud Analytics
def generate_mock_analytics_data():
    # Fraud Detection Trends
    trend_data = []
    for i in range(7): # Last 7 days
        day = (datetime.now() - timedelta(days=i)).strftime("%a")
        total_tx = random.randint(100, 600)
        total_alerts = random.randint(0, 10)
        avg_fraud_rate = random.uniform(0.0, 0.5) # Percentage
        trend_data.append({
            "Day": day,
            "Total Transactions": total_tx,
            "Total Alerts": total_alerts,
            "Avg Fraud Rate": avg_fraud_rate
        })
    fraud_trends_df = pd.DataFrame(trend_data).set_index("Day").sort_index()

    # Risk Score Distribution
    risk_dist_data = {
        "Low (0-39)": random.randint(400, 500),
        "Medium (40-69)": random.randint(0, 50),
        "High (70-89)": random.randint(0, 20),
        "Critical (90-100)": random.randint(0, 5)
    }
    total_risk_dist_tx = sum(risk_dist_data.values())
    risk_dist_df = pd.DataFrame([
        {"Category": k, "Transactions": v, "Percentage": f"{(v/total_risk_dist_tx)*100:.1f}%"}
        for k, v in risk_dist_data.items()
    ])

    # Alert Types (for bar chart)
    alert_types_data = {
        "High Value": random.uniform(0.5, 1.0),
        "Blacklisted Address": random.uniform(0.5, 1.0),
        "Rapid Transactions": random.uniform(0.5, 1.0),
        "Suspicious Pattern": random.uniform(0.5, 1.0)
    }
    alert_types_df = pd.DataFrame([
        {"Type": k, "Value": v} for k, v in alert_types_data.items()
    ])

    # Top Alert Types (for list)
    top_alert_types = [
        {"type": "High Value", "count": random.randint(1, 5), "percentage": f"{random.uniform(10, 30):.1f}%"},
        {"type": "Blacklisted Address", "count": random.randint(1, 5), "percentage": f"{random.uniform(10, 30):.1f}%"},
        {"type": "Rapid Transactions", "count": random.randint(1, 5), "percentage": f"{random.uniform(10, 30):.1f}%"},
        {"type": "Suspicious Pattern", "count": random.randint(1, 5), "percentage": f"{random.uniform(10, 30):.1f}%"},
    ]
    random.shuffle(top_alert_types) # Shuffle for variety

    # Top Risk Addresses
    top_risk_addresses = [
        {"rank": 1, "address": "1A1zP1eP5QG...", "transactions": random.randint(100, 300), "risk_level": "high"},
        {"rank": 2, "address": "3FUgJcM4uJG...", "transactions": random.randint(50, 200), "risk_level": "critical"},
        {"rank": 3, "address": "bc1qxwz7y8...", "transactions": random.randint(20, 100), "risk_level": "high"},
    ]

    return fraud_trends_df, risk_dist_df, alert_types_df, top_alert_types, top_risk_addresses


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


elif page_selection == "Transactions":
    st.header("Transaction Monitor")
    st.markdown("Real-time Bitcoin transaction analysis and fraud detection")

    # Top row with refresh/export buttons
    top_row_cols = st.columns([0.7, 0.1, 0.1, 0.1])
    with top_row_cols[1]:
        st.button("Refresh", key="tx_monitor_refresh_btn")
    with top_row_cols[2]:
        st.button("Export", key="tx_monitor_export_btn")
    
    st.markdown("---")

    # Metrics for Transaction Monitor
    tx_metric_cols = st.columns(5)
    total_tx_count = 220 # Mock value
    live_tx_count = 20 # Mock value
    flagged_tx_count = 0 # Mock value
    high_risk_tx_count = 0 # Mock value
    total_tx_value = 182.64 # Mock value

    with tx_metric_cols[0]:
        st.metric(label="Total Transactions", value=total_tx_count, delta="20 Live")
    with tx_metric_cols[1]:
        st.metric(label="Live", value=live_tx_count)
    with tx_metric_cols[2]:
        st.metric(label="Flagged", value=flagged_tx_count)
    with tx_metric_cols[3]:
        st.metric(label="High Risk", value=high_risk_tx_count)
    with tx_metric_cols[4]:
        st.metric(label="Total Value", value=f"{total_tx_value:.2f} BTC")

    st.markdown("---")

    # Search and Filter Row
    search_filter_cols = st.columns([0.5, 0.15, 0.15, 0.15, 0.05])
    with search_filter_cols[0]:
        st.text_input("Search by hash, address...", key="tx_search_input", label_visibility="collapsed")
    with search_filter_cols[1]:
        st.selectbox("All Status", ["All Status", "Confirmed", "Pending"], key="tx_status_filter")
    with search_filter_cols[2]:
        st.selectbox("All Risk", ["All Risk", "Low", "Medium", "High", "Critical"], key="tx_risk_filter")
    with search_filter_cols[3]:
        st.selectbox("All Time", ["All Time", "Last Hour", "Last 24h", "Last Week"], key="tx_time_filter")

    st.markdown("---")

    # Transaction Table and Details
    tx_table_col, tx_details_col = st.columns([0.7, 0.3])

    with tx_table_col:
        st.markdown("### Transactions")
        transactions_df = generate_mock_transaction_data()
        
        # Manually render DataFrame to apply custom styling per row/cell
        st.markdown("""
        <div class="stDataFrame">
            <table>
                <thead>
                    <tr>
                        <th>Transaction</th>
                        <th>Amount</th>
                        <th>Risk</th>
                        <th>Status</th>
                        <th>Time</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        """, unsafe_allow_html=True)
        
        for index, row in transactions_df.iterrows():
            risk_class = row["Risk_Level"] # Use the Risk_Level for CSS class
            status_class = row["Status"]
            
            st.markdown(f"""
                <tr>
                    <td>
                        <div class="tx-hash">{row["Transaction"].split('\n')[0]}</div>
                        <div class="tx-from">{row["Transaction"].split('\n')[1]}</div>
                    </td>
                    <td>
                        <div class="tx-amount">{row["Amount"].split('\n')[0]}</div>
                        <div class="tx-usd">{row["Amount"].split('\n')[1]}</div>
                    </td>
                    <td><span class="risk-score {risk_class}">{row["Risk"]}</span></td>
                    <td><span class="tx-status {status_class}">{row["Status"]}</span></td>
                    <td><div class="tx-time">{row["Time"]}</div></td>
                    <td>{row["Actions"]}</td>
                </tr>
            """, unsafe_allow_html=True)
        
        st.markdown("""
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with tx_details_col:
        st.markdown("### ") # Empty header for alignment
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 20px; border-radius: 10px; border: 1px solid #444; height: 100%;">
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
                <img src="https://placehold.co/80x80/000/FFF?text=₿" style="border-radius: 50%; margin-bottom: 15px;">
                <p style="text-align: center; color: #bbb;">Select a transaction to view details</p>
            </div>
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

    # Metrics for Security Alerts
    alert_metric_cols = st.columns(4)
    total_alerts_count = 4 # Mock value
    open_alerts_count = 2 # Mock value
    critical_alerts_count = 2 # Mock value
    investigating_alerts_count = 1 # Mock value

    with alert_metric_cols[0]:
        st.metric(label="Total Alerts", value=total_alerts_count)
    with alert_metric_cols[1]:
        st.metric(label="Open", value=open_alerts_count)
    with alert_metric_cols[2]:
        st.metric(label="Critical", value=critical_alerts_count)
    with alert_metric_cols[3]:
        st.metric(label="Investigating", value=investigating_alerts_count)

    st.markdown("---")

    # Search and Filter Row for Alerts
    alert_search_filter_cols = st.columns([0.4, 0.2, 0.2, 0.2])
    with alert_search_filter_cols[0]:
        st.text_input("Search alerts...", key="alert_search_input", label_visibility="collapsed")
    with alert_search_filter_cols[1]:
        st.selectbox("All Status", ["All Status", "Open", "Closed", "Investigating"], key="alert_status_filter")
    with alert_search_filter_cols[2]:
        st.selectbox("All Severity", ["All Severity", "Low", "Medium", "High", "Critical"], key="alert_severity_filter")
    with alert_search_filter_cols[3]:
        st.selectbox("All Types", ["All Types", "Smurfing", "High Value", "Blacklisted Address", "Rapid Transactions", "Suspicious Pattern"], key="alert_type_filter")

    st.markdown("---")

    # Alert List and Details
    alert_list_col, alert_details_col = st.columns([0.7, 0.3])

    with alert_list_col:
        st.markdown("### ") # Empty header for alignment
        # Fetch alerts from Neo4j for the list
        alerts_data = []
        if neo4j_driver:
            try:
                with neo4j_driver.session() as session:
                    query = """
                    MATCH (tx:Transaction)
                    WHERE tx.ml_fraud_score IS NOT NULL AND tx.ml_fraud_score > 0.0
                       OR tx.is_smurfing_rule = true
                    RETURN tx
                    ORDER BY tx.alert_timestamp_ms DESC
                    LIMIT 100
                    """
                    result = session.run(query)
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
            except Exception as e:
                st.error(f"Error fetching alerts from Neo4j: {e}. Please ensure Spark is writing alert data to Neo4j Transaction nodes with relevant properties.")
                alerts_data = [] # Ensure alerts_data is empty on error
        else:
            st.warning("Neo4j driver not connected. Cannot fetch live alerts.")
            alerts_data = [] # Ensure alerts_data is empty if no driver

        # Generate mock alerts if no live data or for demonstration
        if not alerts_data:
            st.info("No live alerts from Neo4j. Displaying mock alerts for demonstration.")
            alerts_data = [
                {
                    "transaction_hash": "0xabc123def4567890abc123def4567890abc123def4567890",
                    "ml_fraud_score": 0.95, "is_smurfing_rule": True,
                    "alert_timestamp_ms": int(time.time() * 1000) - random.randint(10000, 3600000),
                    "type": "High Value",
                    "description": "High-value transaction with suspicious pattern indicators",
                    "risk_score_display": "95"
                },
                {
                    "transaction_hash": "0xdef456ghi7890123def456ghi7890123def456ghi7890123",
                    "ml_fraud_score": 0.90, "is_smurfing_rule": False,
                    "alert_timestamp_ms": int(time.time() * 1000) - random.randint(10000, 3600000),
                    "type": "Blacklisted Address",
                    "description": "Transaction involving known blacklisted address with mixing service connection",
                    "risk_score_display": "90"
                },
                {
                    "transaction_hash": "0x1234567890abcdef1234567890abcdef1234567890abcd",
                    "ml_fraud_score": 0.75, "is_smurfing_rule": False,
                    "alert_timestamp_ms": int(time.time() * 1000) - random.randint(10000, 3600000),
                    "type": "Rapid Transactions",
                    "description": "Rapid transaction pattern detected from source address",
                    "risk_score_display": "75"
                },
                {
                    "transaction_hash": "0x567890abcdef1234567890abcdef1234567890abcdef",
                    "ml_fraud_score": 0.55, "is_smurfing_rule": False,
                    "alert_timestamp_ms": int(time.time() * 1000) - random.randint(10000, 3600000),
                    "type": "Suspicious Pattern",
                    "description": "Unusual transaction timing pattern",
                    "risk_score_display": "55"
                }
            ]
            # Convert timestamps for mock data
            for alert in alerts_data:
                alert['alert_timestamp_readable'] = pd.to_datetime(alert['alert_timestamp_ms'], unit='ms').strftime("%b %d, %H:%M")
                if alert['ml_fraud_score'] > 0.9:
                    alert['severity_level'] = 'critical'
                elif alert['ml_fraud_score'] > 0.7:
                    alert['severity_level'] = 'high'
                elif alert['ml_fraud_score'] > 0.5:
                    alert['severity_level'] = 'medium'
                else:
                    alert['severity_level'] = 'low'
                
        # Display alerts as cards
        if alerts_data:
            for alert in alerts_data:
                st.markdown(f"""
                <div class="alert-list-card">
                    <div class="alert-content">
                        <h5>
                            <span class="alert-category {alert.get('severity_level', 'low')}">{alert.get('severity_level', 'low').capitalize()}</span>
                            {alert.get('type', 'Unknown Alert')}
                        </h5>
                        <p>{alert.get('description', 'No description available.')}</p>
                        <p class="alert-meta">Risk: {alert.get('risk_score_display', 'N/A')} • {alert.get('alert_timestamp_readable', 'N/A')}</p>
                    </div>
                    <div class="alert-actions">
                        <span style="font-size: 1.5rem; cursor: pointer;">&#128065;</span> <!-- Eye icon -->
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No alerts to display. Please ensure Spark is processing data and writing alert-related transaction properties to Neo4j.")

    with alert_details_col:
        st.markdown("### ") # Empty header for alignment
        st.markdown("""
        <div style="background-color: #2a2a2a; padding: 20px; border-radius: 10px; border: 1px solid #444; height: 100%;">
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
                <img src="https://placehold.co/80x80/000/FFF?text=! " style="border-radius: 50%; margin-bottom: 15px;">
                <p style="text-align: center; color: #bbb;">Select an alert to view details</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


elif page_selection == "Analytics":
    st.header("Fraud Analytics")
    st.markdown("Advanced insights and trends in Bitcoin fraud detection")

    # Top row with date filter and export button
    analytics_top_row_cols = st.columns([0.7, 0.15, 0.15])
    with analytics_top_row_cols[1]:
        st.selectbox("Last 7 days", ["Last 7 days", "Last 30 days", "Last 90 days", "All time"], key="analytics_time_filter")
    with analytics_top_row_cols[2]:
        st.button("Export Report", key="analytics_export_btn")
    
    st.markdown("---")

    # Top Metrics for Analytics
    analytics_metric_cols = st.columns(6)
    total_transactions_analytics = 500 # Mock value
    total_alerts_analytics = 4 # Mock value
    fraud_rate = 0.8 # Mock value
    avg_risk_score_analytics = 9.8 # Mock value
    critical_alerts_analytics = 2 # Mock value
    resolution_rate = 25.0 # Mock value
    high_risk_addresses_analytics = 2 # Mock value

    with analytics_metric_cols[0]:
        st.metric(label="Total Transactions", value=total_transactions_analytics, delta="Monitored")
    with analytics_metric_cols[1]:
        st.metric(label="Total Alerts", value=total_alerts_analytics, delta="Generated")
    with analytics_metric_cols[2]:
        st.metric(label="Fraud Rate", value=f"{fraud_rate:.1f}%", delta="Detection rate")
    with analytics_metric_cols[3]:
        st.metric(label="Avg Risk Score", value=f"{avg_risk_score_analytics:.1f}", delta="0-100 scale")
    with analytics_metric_cols[4]:
        st.metric(label="Critical Alerts", value=critical_alerts_analytics, delta="High priority")
    with analytics_metric_cols[5]:
        st.metric(label="Resolution Rate", value=f"{resolution_rate:.1f}%", delta="Resolved alerts")
        # st.metric(label="High Risk Addresses", value=high_risk_addresses_analytics, delta="Monitored") # From screenshot, but only 6 metrics fit well

    st.markdown("---")

    # Fraud Detection Trends
    st.subheader("📈 Fraud Detection Trends")
    fraud_trends_df, risk_dist_df, alert_types_df, top_alert_types, top_risk_addresses = generate_mock_analytics_data()
    
    trends_chart_cols = st.columns([0.2, 0.8])
    with trends_chart_cols[0]:
        st.metric(label="Total Transactions", value=fraud_trends_df["Total Transactions"].sum())
        st.metric(label="Total Alerts", value=fraud_trends_df["Total Alerts"].sum())
        st.metric(label="Avg Fraud Rate", value=f"{fraud_trends_df['Avg Fraud Rate'].mean():.1f}%")
    with trends_chart_cols[1]:
        st.line_chart(fraud_trends_df[["Total Transactions", "Total Alerts", "Avg Fraud Rate"]], use_container_width=True)

    st.markdown("---")

    # Risk Score Distribution
    st.subheader("📊 Risk Score Distribution")
    risk_dist_chart_cols = st.columns(2)
    with risk_dist_chart_cols[0]:
        # Streamlit doesn't have a native donut chart, using a bar chart to represent distribution
        st.bar_chart(risk_dist_df.set_index("Category")["Transactions"], use_container_width=True)
    with risk_dist_chart_cols[1]:
        st.markdown("#### ") # Empty header for alignment
        for index, row in risk_dist_df.iterrows():
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <span class="risk-distribution-label">{row['Category']}</span>
                <span class="risk-distribution-value">{row['Transactions']} transactions ({row['Percentage']})</span>
            </div>
            """, unsafe_allow_html=True)
        # Add a placeholder for the circle chart if needed
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 150px;">
            <div style="width: 100px; height: 100px; border-radius: 50%; background: conic-gradient(
                #28a745 0% 70%, /* Low */
                #17a2b8 70% 85%, /* Medium */
                #ffc107 85% 95%, /* High */
                #dc3545 95% 100% /* Critical */
            ); border: 5px solid #444;"></div>
        </div>
        """, unsafe_allow_html=True)


    st.markdown("---")

    # Alert Analysis and Top Risk Addresses
    alert_analysis_col, top_risk_addresses_col = st.columns(2)

    with alert_analysis_col:
        st.subheader("⚠️ Alert Analysis")
        st.markdown("#### Alert Types")
        st.bar_chart(alert_types_df.set_index("Type"), use_container_width=True)

        st.markdown("#### Severity Breakdown")
        severity_breakdown_cols = st.columns(3)
        with severity_breakdown_cols[0]:
            st.markdown("""
            <div class="analytics-card">
                <p class="analytics-metric-label">Critical</p>
                <p class="analytics-metric-value">2</p>
                <p class="analytics-metric-delta">50.0%</p>
            </div>
            """, unsafe_allow_html=True)
        with severity_breakdown_cols[1]:
            st.markdown("""
            <div class="analytics-card">
                <p class="analytics-metric-label">High</p>
                <p class="analytics-metric-value">1</p>
                <p class="analytics-metric-delta">25.0%</p>
            </div>
            """, unsafe_allow_html=True)
        with severity_breakdown_cols[2]:
            st.markdown("""
            <div class="analytics-card">
                <p class="analytics-metric-label">Medium</p>
                <p class="analytics-metric-value">1</p>
                <p class="analytics-metric-delta">25.0%</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("#### Top Alert Types")
        for i, alert_type in enumerate(top_alert_types):
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <span style="font-weight: bold; margin-right: 10px;">{i+1}</span>
                <div style="flex-grow: 1;">
                    <p style="margin: 0; color: #f0f0f0;">{alert_type['type']}</p>
                </div>
                <span style="color: #bbb;">{alert_type['count']}</span>
                <span style="font-size: 0.8rem; color: #999; margin-left: 5px;">({alert_type['percentage']})</span>
            </div>
            """, unsafe_allow_html=True)


    with top_risk_addresses_col:
        st.subheader("🎯 Top Risk Addresses")
        for address_info in top_risk_addresses:
            st.markdown(f"""
            <div class="top-risk-address-item">
                <span class="rank">{address_info['rank']}</span>
                <div class="address-info">
                    <div class="address-hash">{address_info['address']}</div>
                    <div class="tx-count">{address_info['transactions']} transactions</div>
                </div>
                <span class="alert-category {address_info['risk_level']}">{address_info['risk_level'].capitalize()}</span>
            </div>
            """, unsafe_allow_html=True)


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
