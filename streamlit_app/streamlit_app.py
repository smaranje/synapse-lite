import streamlit as st
import pandas as pd
import json
import random
import hashlib
import time
from datetime import datetime, timedelta
import html

# Configuration
USE_DUMMY_DATA = True  # Always use dummy data for this demo
BTC_USD_RATE = 65000  # Fixed BTC to USD conversion rate
st.set_page_config(layout="wide", page_title="Synapse-Lite Fraud Detector")

# Custom CSS (unchanged from original)
st.markdown("""
    <style>
    .main {
        background-color: #1a1a1a;
        color: #e0e0e0;
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
        background-color: #4CAF50;
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

# --- Helper Functions ---

def get_risk_level(ml_score, is_smurfing_rule):
    """Determine risk level based on ML score and smurfing rule."""
    ml_score = ml_score if ml_score is not None else 0.0
    is_smurfing_rule = is_smurfing_rule if is_smurfing_rule is not None else False
    if is_smurfing_rule or ml_score >= 0.9:
        return "Critical"
    elif ml_score >= 0.7:
        return "High"
    elif ml_score >= 0.4:
        return "Medium"
    return "Low"

@st.cache_data(ttl=5)
def generate_dummy_transactions(limit=10):
    """Generate dummy transaction data."""
    current_time = datetime.now()
    transactions = []
    
    for i in range(limit):
        tx_hash = hashlib.sha256(f"tx_{i}_{int(time.time())}".encode()).hexdigest()
        timestamp = (current_time - timedelta(hours=random.uniform(0, 24))).timestamp() * 1000
        total_input_value = random.uniform(1000000, 1000000000)  # 0.01 to 10 BTC in Satoshis
        total_output_value = total_input_value * random.uniform(0.95, 0.99)
        fee = total_input_value - total_output_value
        ml_score = random.uniform(0.0, 1.0)
        is_smurfing = random.random() > 0.8
        
        transactions.append({
            "Hash": tx_hash,
            "Timestamp": timestamp,
            "Fee": fee,
            "Size": random.randint(200, 2000),
            "NumInputs": random.randint(1, 10),
            "NumOutputs": random.randint(1, 10),
            "TotalInputValue": total_input_value,
            "TotalOutputValue": total_output_value,
            "ML_Score": ml_score,
            "Smurfing_Rule": is_smurfing
        })
    
    df = pd.DataFrame(transactions)
    if not df.empty:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df['TotalInputValueBTC'] = df['TotalInputValue'] / 1e8
        df['TotalOutputValueBTC'] = df['TotalOutputValue'] / 1e8
        df['Risk_Level'] = df.apply(lambda row: get_risk_level(row['ML_Score'], row['Smurfing_Rule']), axis=1)
        df['Amount'] = df.apply(lambda row: f"{row['TotalOutputValueBTC']:.4f} BTC\n${row['TotalOutputValueBTC'] * BTC_USD_RATE:,.2f}", axis=1)
        df['Risk'] = df.apply(lambda row: f"{row['Risk_Level']} ({int(row['ML_Score']*100)})", axis=1)
        df['Status'] = 'confirmed'
        df['Time'] = df['Timestamp'].dt.strftime("%H:%M:%S")
        df['Actions'] = '🔗'
    return df

@st.cache_data(ttl=10)
def generate_dummy_alerts(limit=100):
    """Generate dummy alert data for suspicious transactions."""
    current_time = datetime.now()
    alerts = []
    
    for i in range(limit):
        ml_score = random.uniform(0.4, 1.0)
        is_smurfing = random.random() > 0.7
        if ml_score < 0.5 and not is_smurfing:
            continue
        tx_hash = hashlib.sha256(f"alert_{i}_{int(time.time())}".encode()).hexdigest()
        timestamp = (current_time - timedelta(hours=random.uniform(0, 24))).timestamp() * 1000
        total_input_value = random.uniform(1000000, 1000000000)
        total_output_value = total_input_value * random.uniform(0.95, 0.99)
        fee = total_input_value - total_output_value
        
        alerts.append({
            "Hash": tx_hash,
            "Timestamp": timestamp,
            "ML_Score": ml_score,
            "Smurfing_Rule": is_smurfing,
            "Fee": fee,
            "Size": random.randint(200, 2000),
            "FeePerByte": fee / random.randint(200, 2000),
            "TotalInputValue": total_input_value,
            "TotalOutputValue": total_output_value,
            "SHAP_Features": json.dumps({
                "input_count": random.uniform(-0.1, 0.1),
                "output_count": random.uniform(-0.1, 0.1),
                "fee_ratio": random.uniform(-0.05, 0.05),
                "amount_ratio": random.uniform(-0.1, 0.1)
            })
        })
    
    df = pd.DataFrame(alerts)
    if not df.empty:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df['Risk_Level'] = df.apply(lambda row: get_risk_level(row['ML_Score'], row['Smurfing_Rule']), axis=1)
    return df.head(limit)

@st.cache_data(ttl=60)
def generate_dummy_analytics_data():
    """Generate dummy analytics data for metrics and trends."""
    current_time = datetime.now()
    metrics = {
        "total_transactions": random.randint(1000, 5000),
        "active_alerts": random.randint(10, 50),
        "critical_alerts": random.randint(5, 20),
        "avg_risk_score": random.uniform(50, 80),
        "high_risk_addresses": random.randint(5, 15),
        "total_alerts": random.randint(50, 200)
    }
    
    # Average Risk Score Trends
    avg_risk_data = []
    high_risk_tx_data = []
    for hour in range(24):
        hour_ago = current_time - timedelta(hours=hour)
        hour_label = hour_ago.strftime("%H:00")
        avg_risk_data.append({"Hour": hour_label, "Average Risk Score": random.uniform(40, 80)})
        high_risk_tx_data.append({"Hour": hour_label, "High Risk Transactions": random.randint(0, 10)})
    
    avg_risk_trends_df = pd.DataFrame(avg_risk_data).set_index("Hour").sort_index()
    high_risk_tx_trends_df = pd.DataFrame(high_risk_tx_data).set_index("Hour").sort_index()
    
    # Risk Score Distribution
    total_dist_tx = random.randint(100, 500)
    risk_distribution_data = [
        {"Category": "Low", "Transactions": int(total_dist_tx * 0.5), "Percentage": "50.0%"},
        {"Category": "Medium", "Transactions": int(total_dist_tx * 0.3), "Percentage": "30.0%"},
        {"Category": "High", "Transactions": int(total_dist_tx * 0.15), "Percentage": "15.0%"},
        {"Category": "Critical", "Transactions": int(total_dist_tx * 0.05), "Percentage": "5.0%"}
    ]
    risk_distribution_df = pd.DataFrame(risk_distribution_data)
    
    # Top Alert Types
    smurfing_count = random.randint(10, 50)
    high_ml_count = random.randint(5, 30)
    total_alerts = metrics["total_alerts"]
    top_alert_types_list = [
        {"type": "Smurfing Rule", "count": smurfing_count, "percentage": f"{(smurfing_count / total_alerts)*100:.1f}%"},
        {"type": "High ML Score", "count": high_ml_count, "percentage": f"{(high_ml_count / total_alerts)*100:.1f}%"}
    ]
    
    # Top Risk Addresses
    top_risk_addresses_list = [
        {
            "rank": i+1,
            "address": hashlib.sha256(f"addr_{i}_{int(time.time())}".encode()).hexdigest()[:12],
            "transactions": random.randint(5, 20),
            "risk_level": random.choice(["High", "Critical"])
        } for i in range(5)
    ]
    
    return metrics, avg_risk_trends_df, high_risk_tx_trends_df, risk_distribution_df, top_alert_types_list, top_risk_addresses_list

def generate_mock_sar(alert_data):
    """Generate a mock SAR draft."""
    tx_hash = alert_data.get("transaction_hash", "N/A")
    ml_score = alert_data.get("ml_fraud_score", 0.0)
    is_smurfing = alert_data.get("is_smurfing_rule", False)
    amount_btc = float(alert_data.get("total_output_value", 0)) / 1e8
    description = (
        f"Suspicious transaction detected (Hash: {tx_hash[:12]}...). "
        f"Transaction value: {amount_btc:.4f} BTC (${amount_btc * BTC_USD_RATE:,.2f} USD). "
        f"ML Fraud Score: {ml_score:.2f}. "
        f"Smurfing Rule Triggered: {is_smurfing}. "
        "This transaction exhibits patterns consistent with potential money laundering or fraud. "
        "Further investigation recommended."
    )
    return description

# Sidebar Navigation
with st.sidebar:
    st.image("https://placehold.co/150x50/000/FFF?text=Synapse-Lite", use_container_width=True)
    st.markdown("## Navigation")
    page_selection = st.radio(
        "Go to",
        ["Dashboard", "Transactions", "Alerts", "Analytics", "Settings", "Debug Data"],
        index=0
    )
    st.markdown("---")
    st.info("Fraud detection@synapse.com")

# --- Main Content Area ---
if page_selection == "Dashboard":
    st.header("Fraud Detection Dashboard")
    st.markdown("Real-time Bitcoin transaction monitoring and threat analysis")
    st.markdown("<p style='color:#28a745; font-weight:bold;'>● Live Monitoring Active</p>", unsafe_allow_html=True)

    # Top Metrics
    st.markdown("---")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    metrics, _, _, _, _, _ = generate_dummy_analytics_data()
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
            st.cache_data.clear()
            st.rerun()
    
    with mempool_col1:
        with st.spinner("Fetching live mempool data..."):
            live_mempool_df = generate_dummy_transactions(limit=10)
            if not live_mempool_df.empty:
                display_cols = ['Hash', 'Amount', 'Risk', 'Status', 'Time', 'Actions']
                st.dataframe(live_mempool_df[display_cols], hide_index=True, use_container_width=True)
            else:
                st.info("No recent transactions available.")

    st.markdown("---")

    # Active Alerts
    st.subheader("🚨 Active Alerts")
    active_alerts_col1, active_alerts_col2, active_alerts_col3 = st.columns([0.1, 0.1, 0.8])
    active_alerts_display_df = generate_dummy_alerts(limit=5)
    active_alerts_display_df["Risk_Level"] = active_alerts_display_df.apply(
        lambda row: get_risk_level(row["ML_Score"], row["Smurfing_Rule"]), axis=1
    )
    critical_alerts_count = active_alerts_display_df.query("Risk_Level == 'Critical'").shape[0]
    high_alerts_count = active_alerts_display_df.query("Risk_Level == 'High'").shape[0]

    with active_alerts_col1:
        st.markdown(f"<p class='alert-category critical'>{critical_alerts_count} Critical</p>", unsafe_allow_html=True)
    with active_alerts_col2:
        st.markdown(f"<p class='alert-category high'>{high_alerts_count} Open</p>", unsafe_allow_html=True)
    
    if not active_alerts_display_df.empty:
        alerts_data_df_sorted = active_alerts_display_df.sort_values(
            by=['Risk_Level', 'Timestamp'],
            key=lambda x: x.map({"Critical": 0, "High": 1, "Medium": 2, "Low": 3}),
            ascending=[True, False]
        )
        for _, alert in alerts_data_df_sorted.iterrows():
            alert_category = alert['Risk_Level'].lower()
            description = "Unusual transaction pattern detected."
            if alert.get("Smurfing_Rule"):
                description = "Smurfing rule triggered: multiple small outputs."
            elif alert.get("ML_Score", 0) >= 0.9:
                description = "High-value transaction with suspicious ML score (Critical)."
            elif alert.get("ML_Score", 0) >= 0.7:
                description = "High-value transaction with suspicious ML score (High)."
            elif alert.get("ML_Score", 0) >= 0.4:
                description = "Transaction with medium ML score."
            
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
        st.info("No active alerts found.")
    
    st.button("View All Alerts", key="view_all_alerts_btn")
    st.markdown("---")

    # Risk Analysis Trends
    st.subheader("📈 Risk Analysis Trends")
    st.markdown("---")
    _, avg_risk_trends_df, high_risk_tx_trends_df, _, _, _ = generate_dummy_analytics_data()
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

    # Top Row
    top_row_cols = st.columns([0.7, 0.1, 0.1, 0.1])
    with top_row_cols[1]:
        if st.button("Refresh", key="tx_monitor_refresh_btn"):
            st.cache_data.clear()
            st.rerun()
    with top_row_cols[2]:
        st.button("Export", key="tx_monitor_export_btn")

    st.markdown("---")

    # Metrics
    tx_metric_cols = st.columns(5)
    metrics_tx, _, _, _, _, _ = generate_dummy_analytics_data()
    with tx_metric_cols[0]:
        st.metric(label="Total Transactions", value=metrics_tx["total_transactions"])
    with tx_metric_cols[1]:
        st.metric(label="Live (Approx)", value=len(generate_dummy_transactions(limit=50)))
    with tx_metric_cols[2]:
        st.metric(label="Flagged (Alerts)", value=metrics_tx["total_alerts"])
    with tx_metric_cols[3]:
        st.metric(label="High Risk (ML/Rule)", value=metrics_tx["critical_alerts"])
    with tx_metric_cols[4]:
        total_value = sum(generate_dummy_transactions(limit=50)['TotalOutputValue']) / 1e8
        st.metric(label="Total Value (BTC)", value=f"{total_value:.2f}")

    st.markdown("---")

    # Search and Filter
    search_filter_cols = st.columns([0.5, 0.15, 0.15, 0.15, 0.05])
    with search_filter_cols[0]:
        transaction_hash_search = st.text_input("Search by hash, address...", key="tx_search_input", label_visibility="collapsed")
    with search_filter_cols[1]:
        tx_status_filter = st.selectbox("All Status", ["All Status", "Confirmed", "Pending"], key="tx_status_filter")
    with search_filter_cols[2]:
        tx_risk_filter = st.selectboxligere("All Risk", ["All Risk", "Low", "Medium", "High", "Critical"], key="tx_risk_filter")
    with search_filter_cols[3]:
        tx_time_filter = st.selectbox("All Time", ["All Time", "Last Hour", "Last 24h", "Last Week"], key="tx_time_filter")

    st.markdown("---")

    # Transaction Table and Details
    tx_table_col, tx_details_col = st.columns([0.7, 0.3])
    with tx_table_col:
        st.markdown("### Transactions")
        with st.spinner("Fetching transactions..."):
            transactions_df = generate_dummy_transactions(limit=50)
            if transaction_hash_search:
                transactions_df = transactions_df[transactions_df['Hash'].str.contains(transaction_hash_search, case=False, na=False)]
            if tx_status_filter != "All Status":
                transactions_df = transactions_df[transactions_df['Status'] == tx_status_filter.lower()]
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
                for _, row in transactions_df.iterrows():
                    risk_class = row["Risk_Level"].lower()
                    status_class = row["Status"].lower()
                    st.markdown(f"""
                        <tr>
                            <td>
                                <div class="tx-hash">{html.escape(row["Hash"][:12])}...</div>
                                <div class="tx-from">Inputs: {row['NumInputs']} | Outputs: {row['NumOutputs']}</div>
                            </td>
                            <td>
                                <div class="tx-amount">{html.escape(f"{row['TotalOutputValueBTC']:.4f} BTC")}</div>
                                <div class="tx-usd">{html.escape(f"${row['TotalOutputValueBTC'] * BTC_USD_RATE:,.2f}")}</div>
                            </td>
                            <td><span class="risk-score {risk_class}">{html.escape(row["Risk"])}</span></td>
                            <td><span class="tx-status {status_class}">{html.escape(row["Status"])}</span></td>
                            <td><div class="tx-time">{html.escape(row["Timestamp"].strftime("%b %d, %H:%M"))}</div></td>
                            <td><button onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', key: 'selected_tx_hash', value: '{row['Hash']}'}}, '*')" style="background:none; border:none; cursor:pointer; font-size:1.2rem;">🔗</button></td>
                        </tr>
                    """, unsafe_allow_html=True)
                st.markdown("</tbody></table></div>", unsafe_allow_html=True)
            else:
                st.info("No transactions found matching your criteria.")

    with tx_details_col:
        st.markdown("### Transaction Details")
        if 'selected_tx_hash' not in st.session_state:
            st.session_state['selected_tx_hash'] = None
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
        selected_tx_hash = st.session_state.selected_tx_hash
        if selected_tx_hash:
            with st.spinner(f"Fetching details for {selected_tx_hash[:8]}..."):
                tx_df = generate_dummy_transactions(limit=50)
                tx = tx_df[tx_df['Hash'] == selected_tx_hash]
                if not tx.empty:
                    tx = tx.iloc[0]
                    st.subheader(f"Transaction: {tx['Hash'][:12]}...")
                    st.json({
                        "hash": tx['Hash'],
                        "timestamp": tx['Timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                        "fee": tx['Fee'],
                        "size": tx['Size'],
                        "num_inputs": tx['NumInputs'],
                        "num_outputs": tx['NumOutputs'],
                        "total_input_value": tx['TotalInputValue'],
                        "total_output_value": tx['TotalOutputValue'],
                        "ml_fraud_score": tx['ML_Score'],
                        "is_smurfing_rule": tx['Smurfing_Rule']
                    })
                    st.markdown("##### Involved Addresses:")
                    inputs = [hashlib.sha256(f"input_addr_{i}".encode()).hexdigest()[:12] for i in range(int(tx['NumInputs']))]
                    outputs = [hashlib.sha256(f"output_addr_{i}".encode()).hexdigest()[:12] for i in range(int(tx['NumOutputs']))]
                    if inputs:
                        st.write("**Input Addresses:**")
                        for addr in inputs:
                            st.code(addr)
                    else:
                        st.write("**No Input Addresses.**")
                    if outputs:
                        st.write("**Output Addresses:**")
                        for addr in outputs:
                            st.code(addr)
                    else:
                        st.write("**No Output Addresses.**")
                    st.markdown("##### SHAP Feature Contributions:")
                    shap_features = {
                        "input_count": random.uniform(-0.1, 0.1),
                        "output_count": random.uniform(-0.1, 0.1),
                        "fee_ratio": random.uniform(-0.05, 0.05),
                        "amount_ratio": random.uniform(-0.1, 0.1)
                    }
                    for feature, value in sorted(shap_features.items(), key=lambda x: abs(x[1]), reverse=True):
                        st.write(f"- **{feature}:** {value:.4f}")
                else:
                    st.warning(f"Transaction '{selected_tx_hash}' not found.")
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

    # Top Row
    alert_top_row_cols = st.columns([0.8, 0.2])
    with alert_top_row_cols[1]:
        if st.button("Refresh", key="alerts_refresh_btn_top"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")

    # Metrics
    alert_metric_cols = st.columns(4)
    metrics_alerts, _, _, _, _, _ = generate_dummy_analytics_data()
    with alert_metric_cols[0]:
        st.metric(label="Total Alerts", value=metrics_alerts["total_alerts"])
    with alert_metric_cols[1]:
        st.metric(label="Open (24h)", value=metrics_alerts["active_alerts"])
    with alert_metric_cols[2]:
        st.metric(label="Critical", value=metrics_alerts["critical_alerts"])
    with alert_metric_cols[3]:
        st.metric(label="Investigating", value="N/A")

    st.markdown("---")

    # Search and Filter
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
        st.markdown("### ")
        with st.spinner("Fetching alerts..."):
            alerts_data_df = generate_dummy_alerts(limit=50)
            if alert_hash_search:
                alerts_data_df = alerts_data_df[alerts_data_df['Hash'].str.contains(alert_hash_search, case=False, na=False)]
            if alert_severity_filter != "All Severity":
                alerts_data_df = alerts_data_df[alerts_data_df['Risk_Level'] == alert_severity_filter]
            if alert_type_filter != "All Types":
                if alert_type_filter == "Smurfing Rule":
                    alerts_data_df = alerts_data_df[alerts_data_df['Smurfing_Rule'] == True]
                elif alert_type_filter == "High ML Score":
                    alerts_data_df = alerts_data_df[alerts_data_df['ML_Score'] >= 0.9]

            if not alerts_data_df.empty:
                alerts_data_df['Sort_Order'] = alerts_data_df['Risk_Level'].map({"Critical": 0, "High": 1, "Medium": 2, "Low": 3})
                alerts_data_df = alerts_data_df.sort_values(by=['Sort_Order', 'Timestamp'], ascending=[True, False])
                for _, alert in alerts_data_df.iterrows():
                    alert_category = alert['Risk_Level'].lower()
                    description = "Unusual transaction pattern detected."
                    if alert.get("Smurfing_Rule"):
                        description = "Smurfing rule triggered: multiple small outputs."
                    elif alert.get("ML_Score", 0) >= 0.9:
                        description = "High-value transaction with suspicious ML score (Critical)."
                    elif alert.get("ML_Score", 0) >= 0.7:
                        description = "High-value transaction with suspicious ML score (High)."
                    elif alert.get("ML_Score", 0) >= 0.4:
                        description = "Transaction with medium ML score."
                    
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
        selected_alert_hash = st.session_state.selected_alert_hash
        if selected_alert_hash:
            with st.spinner(f"Fetching alert details for {selected_alert_hash[:8]}..."):
                alert_df = generate_dummy_alerts(limit=50)
                alert = alert_df[alert_df['Hash'] == selected_alert_hash]
                if not alert.empty:
                    alert = alert.iloc[0]
                    st.subheader(f"Alert: {alert['Hash'][:12]}...")
                    st.markdown(f"**ML Fraud Score:** {alert['ML_Score']:.2f}")
                    st.markdown(f"**Smurfing Rule Triggered:** {alert['Smurfing_Rule']}")
                    st.markdown(f"**Transaction Timestamp:** {alert['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(f"**Total Input Value (BTC):** {float(alert['TotalInputValue']) / 1e8:.4f}")
                    st.markdown(f"**Total Output Value (BTC):** {float(alert['TotalOutputValue']) / 1e8:.4f}")
                    st.markdown(f"**Transaction Fee (BTC):** {float(alert['Fee']) / 1e8:.8f}")
                    st.markdown(f"**Fee Per Byte:** {alert['FeePerByte']:.4f}")
                    st.markdown("##### Involved Addresses:")
                    inputs = [hashlib.sha256(f"input_addr_{i}".encode()).hexdigest()[:12] for i in range(random.randint(1, 5))]
                    outputs = [hashlib.sha256(f"output_addr_{i}".encode()).hexdigest()[:12] for i in range(random.randint(1, 5))]
                    if inputs:
                        st.write("**Input Addresses:**")
                        for addr in inputs:
                            st.code(addr)
                    if outputs:
                        st.write("**Output Addresses:**")
                        for addr in outputs:
                            st.code(addr)
                    st.markdown("##### SHAP Feature Contributions:")
                    try:
                        shap_features = json.loads(alert['SHAP_Features'])
                        for feature, value in sorted(shap_features.items(), key=lambda x: abs(x[1]), reverse=True):
                            st.write(f"- **{feature}:** {value:.4f}")
                    except json.JSONDecodeError:
                        st.write("Invalid SHAP features JSON.")
                    st.markdown("---")
                    st.markdown("##### Generate SAR Draft:")
                    sar_alert_data = {
                        "transaction_hash": alert['Hash'],
                        "ml_fraud_score": alert['ML_Score'],
                        "is_smurfing_rule": alert['Smurfing_Rule'],
                        "num_inputs": random.randint(1, 5),
                        "num_outputs": random.randint(1, 5),
                        "total_input_value": alert['TotalInputValue'],
                        "total_output_value": alert['TotalOutputValue'],
                        "transaction_fee": alert['Fee'],
                        "fee_per_byte": alert['FeePerByte'],
                        "shap_features_json": alert['SHAP_Features']
                    }
                    if st.button("Generate SAR Draft"):
                        with st.spinner("Generating SAR..."):
                            sar_draft = generate_mock_sar(sar_alert_data)
                            st.text_area("SAR Draft", sar_draft, height=300)
                else:
                    st.warning(f"Alert transaction '{selected_alert_hash}' not found.")
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

    # Top Row
    analytics_top_row_cols = st.columns([0.8, 0.2])
    with analytics_top_row_cols[1]:
        if st.button("Refresh", key="analytics_refresh_btn_top"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")

    # Metrics
    analytics_metric_cols = st.columns(4)
    metrics_analytics, _, _, _, _, _ = generate_dummy_analytics_data()
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
    _, avg_risk_trends_df, high_risk_tx_trends_df, _, _, _ = generate_dummy_analytics_data()
    trends_analytics_col1, trends_analytics_col2 = st.columns(2)
    with trends_analytics_col1:
        st.markdown("#### Average Risk Score by Hour")
        if not avg_risk_trends_df.empty:
            st.line_chart(avg_risk_trends_df, use_container_width=True)
        else:
            st.info("No average risk score trend data available.")
    with trends_analytics_col2:
        st.markdown("#### High Risk Transactions")
        if not high_risk_tx_trends_df.empty:
            st.line_chart(high_risk_tx_trends_df, use_container_width=True)
        else:
            st.info("No high risk transaction trend data available.")
    
    st.markdown("---")

    # Risk Score Distribution & Top Alert Types
    risk_dist_col, top_alerts_col = st.columns(2)
    _, _, _, risk_distribution_df, top_alert_types_list, _ = generate_dummy_analytics_data()
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
    _, _, _, _, _, top_risk_addresses_list = generate_dummy_analytics_data()
    if top_risk_addresses_list:
        for item in top_risk_addresses_list:
            st.markdown(f"""
            <div class="top-risk-address-item">
                <span class="rank">#{item['rank']}</span>
                <div class="address-info">
                    <div class="address-hash">{html.escape(item['address'])}...</div>
                    <div class="tx-count">{item['transactions']} High-Risk Transactions</div>
                </div>
                <span class="risk-score {item['risk_level'].lower()}">{item['risk_level'].capitalize()}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No top risk addresses data available.")

elif page_selection == "Settings":
    st.header("Settings")
    st.markdown("Configure application parameters.")
    st.subheader("Data Source")
    st.info("Using dummy data for demonstration. To switch to live data, configure Neo4j and LLM services in a production environment.")
    st.subheader("Data Retention")
    st.write("Dummy data is generated on-demand and cached temporarily.")
    st.markdown("---")
    st.write("For advanced configurations, refer to the project's documentation.")

elif page_selection == "Debug Data":
    st.header("Debug Data")
    st.markdown("Raw transaction data for debugging purposes.")
    debug_col1, debug_col2 = st.columns([0.8, 0.2])
    with debug_col2:
        if st.button("Refresh Debug Data", key="debug_refresh_btn"):
            st.cache_data.clear()
            st.rerun()
    st.markdown("---")
    @st.cache_data(ttl=5)
    def fetch_raw_transactions_for_debug(limit=20):
        """Generate raw dummy transaction data."""
        return generate_dummy_transactions(limit=limit)
    
    raw_transactions_df = fetch_raw_transactions_for_debug()
    if not raw_transactions_df.empty:
        st.write(f"Displaying {len(raw_transactions_df)} raw transactions:")
        st.dataframe(raw_transactions_df, use_container_width=True)
        st.subheader("Timestamp Analysis:")
        if 'Timestamp' in raw_transactions_df.columns:
            st.write("First 5 timestamps:")
            for ts in raw_transactions_df['Timestamp'].head(5):
                dt_object = ts.strftime('%Y-%m-%d %H:%M:%S')
                st.write(f"- Converted: `{dt_object}`")
            st.write(f"Min Timestamp: `{raw_transactions_df['Timestamp'].min()}`")
            st.write(f"Max Timestamp: `{raw_transactions_df['Timestamp'].max()}`")
        else:
            st.warning("No 'Timestamp' column found.")
    else:
        st.info("No raw transaction data available.")