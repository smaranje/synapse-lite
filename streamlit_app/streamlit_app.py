import streamlit as st
import pandas as pd
import json
import random
import hashlib
import time
from datetime import datetime, timedelta
import html
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Configuration
USE_DUMMY_DATA = True
BTC_USD_RATE = 65000
st.set_page_config(
    layout="wide",
    page_title="Synapse-Lite Fraud Detector",
    page_icon="🔷",
    initial_sidebar_state="expanded"
)

# Initialize theme in session state
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'Light'

theme = st.session_state['theme']

# Define CSS variables based on theme (Coinbase color scheme)
if theme == 'Dark':
    st.markdown("""
    <style>
    :root {
        --background-color: #121212;  /* Dark gray background */
        --text-color: #ffffff;        /* White text */
        --card-background: #1f1f1f;   /* Slightly lighter dark for cards */
        --primary-color: #1652F0;     /* Coinbase blue */
        --positive-color: #00C805;    /* Coinbase green */
        --negative-color: #FF4B4B;    /* Coinbase red */
        --neutral-color: #FFA500;     /* Orange for neutral */
        --border-color: #2d3748;      /* Dark border */
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    :root {
        --background-color: #ffffff;  /* White background */
        --text-color: #000000;        /* Black text */
        --card-background: #f0f2f6;   /* Light gray for cards */
        --primary-color: #1652F0;     /* Coinbase blue */
        --positive-color: #00C805;    /* Coinbase green */
        --negative-color: #FF4B4B;    /* Coinbase red */
        --neutral-color: #FFA500;     /* Orange for neutral */
        --border-color: #e2e8f0;      /* Light border */
    }
    </style>
    """, unsafe_allow_html=True)

# Enhanced Custom CSS with Coinbase-inspired design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');

    .main {
        background: var(--background-color);
        color: var(--text-color);
        font-family: 'Montserrat', sans-serif;
    }

    .stApp {
        background: var(--background-color);
    }

    /* Header styling */
    h1 {
        color: var(--text-color);
        font-weight: 700;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }

    h2, h3 {
        color: var(--text-color);
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        letter-spacing: -0.25px;
    }

    /* Sidebar styling (Coinbase design: clean, minimal, clear typography) */
    .css-1d391kg {
        background: var(--card-background);
        border-right: 1px solid var(--border-color);
        padding: 1rem 0;
    }

    .stRadio > label {
        color: var(--text-color);
        font-weight: 500;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    .stRadio > label:hover {
        background: rgba(22, 82, 240, 0.1);  /* Light blue hover */
    }

    /* Metric cards */
    .metric-card {
        background: var(--card-background);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        border-color: var(--primary-color);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin: 0.5rem 0;
    }

    .metric-label {
        font-size: 0.9rem;
        color: var(--text-color);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .metric-delta.positive {
        color: var(--positive-color);
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }

    .metric-delta.negative {
        color: var(--negative-color);
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }

    .metric-delta.neutral {
        color: var(--neutral-color);
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }

    /* Status indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .status-live {
        background: var(--positive-color);
        color: #ffffff;
    }

    .status-warning {
        background: var(--neutral-color);
        color: #ffffff;
    }

    .status-critical {
        background: var(--negative-color);
        color: #ffffff;
    }

    /* Alert cards */
    .alert-card {
        background: var(--card-background);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary-color);
        margin-bottom: 1rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }

    .alert-card:hover {
        transform: translateX(3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }

    .alert-card.critical {
        border-left-color: var(--negative-color);
    }

    .alert-card.high {
        border-left-color: var(--neutral-color);
    }

    .alert-card.medium {
        border-left-color: var(--primary-color);
    }

    .alert-card.low {
        background: var(--card-background);
        border-left-color: var(--positive-color);
    }

    /* Transaction cards */
    .transaction-card {
        background: var(--card-background);
        padding: 1.25rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
    }

    .transaction-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
        border-color: var(--primary-color);
    }

    /* Buttons */
    .stButton > button {
        background: var(--primary-color);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(22, 82, 240, 0.3);
    }

    .stButton > button:hover {
        background: #1242c8;  /* Darker Coinbase blue */
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(22, 82, 240, 0.4);
    }

    /* Risk badges */
    .risk-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .risk-badge.critical {
        background: var(--negative-color);
        color: #ffffff;
    }

    .risk-badge.high {
        background: var(--neutral-color);
        color: #ffffff;
    }

    .risk-badge.medium {
        background: var(--primary-color);
        color: #ffffff;
    }

    .risk-badge.low {
        background: var(--positive-color);
        color: #ffffff;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: var(--text-color);
        font-size: 0.9rem;
        border-top: 1px solid var(--border-color);
        margin-top: 3rem;
    }
    </style>
""", unsafe_allow_html=True)

# Helper Functions (unchanged from original)
def get_risk_level(ml_score, is_smurfing_rule):
    ml_score = ml_score if ml_score is not None else 0.0
    is_smurfing_rule = is_smurfing_rule if is_smurfing_rule is not None else False
    if is_smurfing_rule or ml_score >= 0.9:
        return "Critical"
    elif ml_score >= 0.7:
        return "High"
    elif ml_score >= 0.4:
        return "Medium"
    return "Low"

def create_metric_card(label, value, delta=None, delta_type="neutral"):
    delta_class = f"metric-delta {delta_type}" if delta else ""
    delta_html = f'<div class="{delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

def create_status_indicator(status, text):
    return f'<span class="status-indicator status-{status}">● {text}</span>'

def create_risk_badge(risk_level, score=None):
    score_text = f" ({int(score*100)}%)" if score else ""
    return f'<span class="risk-badge {risk_level.lower()}">{risk_level}{score_text}</span>'

@st.cache_data(ttl=5)
def generate_dummy_transactions(limit=10):
    current_time = datetime.now()
    transactions = []
    for i in range(limit):
        tx_hash = hashlib.sha256(f"tx_{i}_{int(time.time())}".encode()).hexdigest()
        timestamp = (current_time - timedelta(hours=random.uniform(0, 24))).timestamp() * 1000
        total_input_value = random.uniform(1000000, 1000000000)
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
    return df

@st.cache_data(ttl=10)
def generate_dummy_alerts(limit=100):
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
            "TotalOutputValue": total_output_value
        })
    df = pd.DataFrame(alerts)
    if not df.empty:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df['Risk_Level'] = df.apply(lambda row: get_risk_level(row['ML_Score'], row['Smurfing_Rule']), axis=1)
    return df.head(limit)

@st.cache_data(ttl=60)
def generate_analytics_data():
    current_time = datetime.now()
    hours = []
    risk_scores = []
    transaction_counts = []
    alert_counts = []
    for i in range(24):
        hour = current_time - timedelta(hours=i)
        hours.append(hour)
        risk_scores.append(random.uniform(40, 80))
        transaction_counts.append(random.randint(50, 200))
        alert_counts.append(random.randint(0, 15))
    return {
        'hours': hours,
        'risk_scores': risk_scores,
        'transaction_counts': transaction_counts,
        'alert_counts': alert_counts
    }

def create_advanced_charts():
    data = generate_analytics_data()
    template = 'plotly_dark' if st.session_state.get('theme', 'Light') == 'Dark' else 'plotly_white'
    
    fig_risk = go.Figure()
    fig_risk.add_trace(go.Scatter(
        x=data['hours'],
        y=data['risk_scores'],
        mode='lines+markers',
        name='Risk Score',
        line=dict(color='#1652F0', width=3),
        marker=dict(size=8, color='#1652F0'),
        fill='tonexty',
        fillcolor='rgba(22, 82, 240, 0.1)'
    ))
    fig_risk.update_layout(
        title='Risk Score Trend (24h)',
        xaxis_title='Time',
        yaxis_title='Risk Score',
        template=template,
        height=400,
        showlegend=False
    )
    
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Bar(
        x=data['hours'],
        y=data['transaction_counts'],
        name='Transactions',
        marker=dict(color='#00C805', opacity=0.8)
    ))
    fig_volume.update_layout(
        title='Transaction Volume (24h)',
        xaxis_title='Time',
        yaxis_title='Transaction Count',
        template=template,
        height=400,
        showlegend=False
    )
    
    alert_data = generate_dummy_alerts(100)
    risk_counts = alert_data['Risk_Level'].value_counts()
    fig_pie = go.Figure(data=[go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        hole=0.4,
        marker=dict(colors=['#FF4B4B', '#FFA500', '#1652F0', '#00C805'])
    )])
    fig_pie.update_layout(
        title='Alert Distribution by Risk Level',
        template=template,
        height=400
    )
    
    return fig_risk, fig_volume, fig_pie

# Enhanced Sidebar (Coinbase-inspired)
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 1.5rem; margin: 0; color: var(--primary-color); font-weight: 700;">Synapse-Lite</h1>
        <p style="color: var(--text-color); font-size: 0.9rem; margin: 0.5rem 0; font-weight: 500;">Fraud Detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    pages = {
        "🏠 Dashboard": "Dashboard",
        "📊 Transactions": "Transactions",
        "🚨 Alerts": "Alerts",
        "📈 Analytics": "Analytics",
        "⚙️ Settings": "Settings"
    }
    selected_page = st.radio("", list(pages.keys()), index=0)
    page_selection = pages[selected_page]
    
    st.markdown("---")
    
    st.markdown("### System Status")
    st.markdown(create_status_indicator("live", "Monitoring Active"), unsafe_allow_html=True)
    st.markdown(create_status_indicator("warning", "5 Alerts Pending"), unsafe_allow_html=True)
    st.markdown(create_status_indicator("live", "API Connected"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### Quick Stats")
    metrics = {
        "transactions_today": random.randint(1000, 5000),
        "alerts_today": random.randint(10, 50),
        "risk_score": random.uniform(50, 80)
    }
    st.markdown(f"""
    <div style="font-size: 0.9rem; color: var(--text-color);">
        <p>Transactions Today: <strong style="color: var(--primary-color);">{metrics['transactions_today']}</strong></p>
        <p>Alerts Today: <strong style="color: var(--neutral-color);">{metrics['alerts_today']}</strong></p>
        <p>Avg Risk Score: <strong style="color: var(--positive-color);">{metrics['risk_score']:.1f}%</strong></p>
    </div>
    """, unsafe_allow_html=True)

# Main Content
if page_selection == "Dashboard":
    st.markdown("# Fraud Detection Dashboard")
    st.markdown("### Real-time Bitcoin transaction monitoring")
    
    st.markdown(create_status_indicator("live", "Live Monitoring Active"), unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_card("Total Transactions", "2,847", "+12% from yesterday", "positive"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Active Alerts", "23", "5 Critical", "negative"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Risk Score", "67.3%", "+2.1% from avg", "neutral"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("Detection Rate", "94.2%", "Above target", "positive"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("## Real-time Analytics")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        fig_risk, fig_volume, fig_pie = create_advanced_charts()
        st.plotly_chart(fig_risk, use_container_width=True)
    with chart_col2:
        st.plotly_chart(fig_volume, use_container_width=True)
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    recent_col1, recent_col2 = st.columns(2)
    with recent_col1:
        st.markdown("## Recent Transactions")
        transactions = generate_dummy_transactions(5)
        for _, tx in transactions.iterrows():
            risk_level = get_risk_level(tx['ML_Score'], tx['Smurfing_Rule'])
            st.markdown(f"""
            <div class="transaction-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{tx['Hash'][:12]}...</strong>
                        <br>
                        <small style="color: var(--text-color);">{tx['TotalOutputValueBTC']:.4f} BTC</small>
                    </div>
                    <div>
                        {create_risk_badge(risk_level, tx['ML_Score'])}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    with recent_col2:
        st.markdown("## Recent Alerts")
        alerts = generate_dummy_alerts(5)
        for _, alert in alerts.iterrows():
            risk_level = alert['Risk_Level']
            st.markdown(f"""
            <div class="alert-card {risk_level.lower()}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{alert['Hash'][:12]}...</strong>
                        <br>
                        <small style="color: var(--text-color);">{alert['Timestamp'].strftime('%H:%M:%S')}</small>
                    </div>
                    <div>
                        {create_risk_badge(risk_level, alert['ML_Score'])}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif page_selection == "Transactions":
    st.markdown("# Transaction Monitor")
    st.markdown("### Real-time Bitcoin transaction analysis")
    
    control_col1, control_col2, control_col3 = st.columns([2, 1, 1])
    with control_col1:
        search_term = st.text_input("Search transactions", placeholder="Enter hash, address, or amount")
    with control_col2:
        risk_filter = st.selectbox("Risk Level", ["All", "Critical", "High", "Medium", "Low"])
    with control_col3:
        if st.button("Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    transactions = generate_dummy_transactions(20)
    if not transactions.empty:
        if risk_filter != "All":
            transactions = transactions[transactions['Risk_Level'] == risk_filter]
        if search_term:
            transactions = transactions[transactions['Hash'].str.contains(search_term, case=False, na=False)]
        for _, tx in transactions.iterrows():
            risk_level = get_risk_level(tx['ML_Score'], tx['Smurfing_Rule'])
            st.markdown(f"""
            <div class="transaction-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 1.1rem;">{tx['Hash'][:16]}...</div>
                        <div style="color: var(--text-color); font-size: 0.9rem; margin: 0.25rem 0;">
                            {tx['NumInputs']} inputs → {tx['NumOutputs']} outputs
                        </div>
                        <div style="color: var(--primary-color); font-weight: 500;">
                            {tx['TotalOutputValueBTC']:.4f} BTC (${tx['TotalOutputValueBTC'] * BTC_USD_RATE:,.2f})
                        </div>
                    </div>
                    <div style="text-align: right;">
                        {create_risk_badge(risk_level, tx['ML_Score'])}
                        <div style="color: var(--text-color); font-size: 0.8rem; margin-top: 0.5rem;">
                            {tx['Timestamp'].strftime('%H:%M:%S')}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No transactions found matching your criteria.")

elif page_selection == "Alerts":
    st.markdown("# Security Alerts")
    st.markdown("### Monitor and investigate suspicious activity")
    
    alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)
    alerts = generate_dummy_alerts(50)
    critical_count = len(alerts[alerts['Risk_Level'] == 'Critical'])
    high_count = len(alerts[alerts['Risk_Level'] == 'High'])
    medium_count = len(alerts[alerts['Risk_Level'] == 'Medium'])
    low_count = len(alerts[alerts['Risk_Level'] == 'Low'])
    with alert_col1:
        st.markdown(create_metric_card("Critical", str(critical_count), "Immediate action", "negative"), unsafe_allow_html=True)
    with alert_col2:
        st.markdown(create_metric_card("High", str(high_count), "Review required", "neutral"), unsafe_allow_html=True)
    with alert_col3:
        st.markdown(create_metric_card("Medium", str(medium_count), "Monitor closely", "neutral"), unsafe_allow_html=True)
    with alert_col4:
        st.markdown(create_metric_card("Low", str(low_count), "Standard review", "positive"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
    with filter_col1:
        alert_search = st.text_input("Search alerts", placeholder="Enter transaction hash or details")
    with filter_col2:
        severity_filter = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])
    with filter_col3:
        if st.button("Refresh Alerts", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    if not alerts.empty:
        if severity_filter != "All":
            alerts = alerts[alerts['Risk_Level'] == severity_filter]
        if alert_search:
            alerts = alerts[alerts['Hash'].str.contains(alert_search, case=False, na=False)]
        alerts = alerts.sort_values(['Risk_Level', 'Timestamp'], ascending=[True, False])
        for _, alert in alerts.iterrows():
            risk_level = alert['Risk_Level']
            description = "Unusual transaction pattern detected"
            if alert['Smurfing_Rule']:
                description = "Smurfing pattern detected: Multiple small outputs"
            elif alert['ML_Score'] >= 0.9:
                description = "High ML fraud score detected"
            elif alert['ML_Score'] >= 0.7:
                description = "Elevated fraud risk identified"
            st.markdown(f"""
            <div class="alert-card {risk_level.lower()}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">
                            {create_risk_badge(risk_level)} Alert #{alert['Hash'][:8]}...
                        </div>
                        <div style="color: var(--text-color); margin-bottom: 0.75rem;">
                            {description}
                        </div>
                        <div style="color: var(--text-color); font-size: 0.9rem;">
                            <strong>Transaction:</strong> {alert['Hash'][:16]}...<br>
                            <strong>Amount:</strong> {alert['TotalOutputValue']/1e8:.4f} BTC<br>
                            <strong>Time:</strong> {alert['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <button style="background: var(--primary-color); color: white; border: none; border-radius: 8px; padding: 0.5rem 1rem; font-size: 0.9rem; cursor: pointer; font-weight: 500; margin-bottom: 0.5rem;">
                            Investigate
                        </button>
                        <br>
                        <button style="background: var(--positive-color); color: white; border: none; border-radius: 8px; padding: 0.5rem 1rem; font-size: 0.9rem; cursor: pointer; font-weight: 500;">
                            Generate SAR
                        </button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No alerts found matching your criteria.")

elif page_selection == "Analytics":
    st.markdown("# Fraud Analytics")
    st.markdown("### Deep dive into fraud trends and patterns")
    
    fig_risk, fig_volume, fig_pie = create_advanced_charts()
    chart_tabs = st.tabs(["Risk Trends", "Transaction Volume", "Alert Distribution", "Pattern Analysis"])
    
    with chart_tabs[0]:
        st.plotly_chart(fig_risk, use_container_width=True)
        risk_col1, risk_col2 = st.columns(2)
        with risk_col1:
            st.markdown("### Risk Score Statistics")
            data = generate_analytics_data()
            avg_risk = np.mean(data['risk_scores'])
            max_risk = np.max(data['risk_scores'])
            min_risk = np.min(data['risk_scores'])
            st.markdown(f"""
            <div style="background: var(--card-background); padding: 1rem; border-radius: 8px; color: var(--text-color);">
                <p><strong>Average Risk Score:</strong> {avg_risk:.1f}%</p>
                <p><strong>Peak Risk Score:</strong> {max_risk:.1f}%</p>
                <p><strong>Lowest Risk Score:</strong> {min_risk:.1f}%</p>
                <p><strong>Risk Volatility:</strong> {np.std(data['risk_scores']):.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        with risk_col2:
            st.markdown("### Risk Level Distribution")
            alerts = generate_dummy_alerts(100)
            risk_dist = alerts['Risk_Level'].value_counts()
            st.markdown(f"""
            <div style="background: var(--card-background); padding: 1rem; border-radius: 8px; color: var(--text-color);">
                <p>{create_risk_badge('Critical')} {risk_dist.get('Critical', 0)} alerts</p>
                <p>{create_risk_badge('High')} {risk_dist.get('High', 0)} alerts</p>
                <p>{create_risk_badge('Medium')} {risk_dist.get('Medium', 0)} alerts</p>
                <p>{create_risk_badge('Low')} {risk_dist.get('Low', 0)} alerts</p>
            </div>
            """, unsafe_allow_html=True)
    
    with chart_tabs[1]:
        st.plotly_chart(fig_volume, use_container_width=True)
        st.markdown("### Transaction Insights")
        data = generate_analytics_data()
        total_tx = sum(data['transaction_counts'])
        avg_tx = np.mean(data['transaction_counts'])
        insight_col1, insight_col2 = st.columns(2)
        with insight_col1:
            st.markdown(create_metric_card("Total Transactions (24h)", f"{total_tx:,}", f"Avg: {avg_tx:.0f}/hour", "positive"), unsafe_allow_html=True)
        with insight_col2:
            peak_hour = data['hours'][np.argmax(data['transaction_counts'])]
            st.markdown(create_metric_card("Peak Hour", peak_hour.strftime('%H:%M'), f"{max(data['transaction_counts'])} transactions", "neutral"), unsafe_allow_html=True)
    
    with chart_tabs[2]:
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown("### Alert Analysis")
        alerts = generate_dummy_alerts(100)
        analysis_col1, analysis_col2 = st.columns(2)
        with analysis_col1:
            st.markdown("#### Alert Triggers")
            smurfing_alerts = len(alerts[alerts['Smurfing_Rule'] == True])
            ml_alerts = len(alerts[alerts['ML_Score'] >= 0.9])
            st.markdown(f"""
            <div style="background: var(--card-background); padding: 1rem; border-radius: 8px; color: var(--text-color);">
                <p><strong>Smurfing Rule Triggers:</strong> {smurfing_alerts}</p>
                <p><strong>High ML Score Alerts:</strong> {ml_alerts}</p>
                <p><strong>Combined Triggers:</strong> {len(alerts[(alerts['Smurfing_Rule'] == True) & (alerts['ML_Score'] >= 0.9)])}</p>
            </div>
            """, unsafe_allow_html=True)
        with analysis_col2:
            st.markdown("#### Alert Timing")
            hourly_alerts = alerts.groupby(alerts['Timestamp'].dt.hour).size()
            peak_alert_hour = hourly_alerts.idxmax()
            st.markdown(f"""
            <div style="background: var(--card-background); padding: 1rem; border-radius: 8px; color: var(--text-color);">
                <p><strong>Peak Alert Hour:</strong> {peak_alert_hour:02d}:00</p>
                <p><strong>Alerts at Peak:</strong> {hourly_alerts.max()}</p>
                <p><strong>Quietest Hour:</strong> {hourly_alerts.idxmin():02d}:00</p>
            </div>
            """, unsafe_allow_html=True)
    
    with chart_tabs[3]:
        st.markdown("### Pattern Analysis")
        transactions = generate_dummy_transactions(100)
        template = 'plotly_dark' if st.session_state.get('theme', 'Light') == 'Dark' else 'plotly_white'
        fig_ml = px.histogram(
            transactions,
            x='ML_Score',
            nbins=20,
            title='ML Score Distribution',
            color_discrete_sequence=['#1652F0']
        )
        fig_ml.update_layout(template=template)
        st.plotly_chart(fig_ml, use_container_width=True)
        fig_scatter = px.scatter(
            transactions,
            x='TotalOutputValueBTC',
            y='ML_Score',
            color='Risk_Level',
            size='NumOutputs',
            title='Transaction Amount vs Risk Score',
            color_discrete_map={
                'Critical': '#FF4B4B',
                'High': '#FFA500',
                'Medium': '#1652F0',
                'Low': '#00C805'
            }
        )
        fig_scatter.update_layout(template=template)
        st.plotly_chart(fig_scatter, use_container_width=True)

elif page_selection == "Settings":
    st.markdown("# Settings")
    st.markdown("### Configure system parameters and preferences")
    
    settings_tabs = st.tabs(["General", "Security", "Monitoring", "Integrations"])
    with settings_tabs[0]:
        st.markdown("## General Settings")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Display Preferences")
            theme_options = ["Light", "Dark", "Auto"]
            theme_index = theme_options.index(st.session_state['theme'])
            theme = st.selectbox("Theme", theme_options, index=theme_index)
            st.session_state['theme'] = theme
            st.slider("Refresh Rate (seconds)", 1, 60, 5)
            st.checkbox("Show animations", value=True)
            st.checkbox("Enable notifications", value=True)
        with col2:
            st.markdown("### Data Settings")
            st.selectbox("Data Source", ["Demo Data", "Live Feed", "Historical"])
            st.slider("Transaction Limit", 10, 1000, 100)
            st.slider("Alert History (days)", 1, 30, 7)
    with settings_tabs[1]:
        st.markdown("## Security Settings")
        st.markdown("### API Configuration")
        st.text_input("Gemini API Key", type="password", value="••••••••••••••••")
        st.text_input("Neo4j Connection", value="bolt://neo4j:7687")
        st.markdown("### Access Control")
        st.checkbox("Enable audit logging", value=True)
        st.checkbox("Require 2FA", value=False)
        st.selectbox("Session timeout", ["15 min", "30 min", "1 hour", "4 hours"])
    with settings_tabs[2]:
        st.markdown("## Monitoring Settings")
        st.markdown("### Alert Thresholds")
        st.slider("Critical Risk Threshold", 0.0, 1.0, 0.9)
        st.slider("High Risk Threshold", 0.0, 1.0, 0.7)
        st.slider("Medium Risk Threshold", 0.0, 1.0, 0.4)
        st.markdown("### Notification Settings")
        st.checkbox("Email alerts for critical risks", value=True)
        st.checkbox("SMS alerts for system issues", value=False)
        st.text_input("Alert email", value="admin@example.com")
    with settings_tabs[3]:
        st.markdown("## Integration Settings")
        st.markdown("### External Services")
        st.text_input("Webhook URL", placeholder="https://your-webhook.com/alerts")
        st.selectbox("Export Format", ["JSON", "CSV", "XML"])
        st.checkbox("Enable blockchain explorer links", value=True)
        st.markdown("### Database Settings")
        st.text_input("Backup Location", value="/backups/")
        st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"])

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>Synapse-Lite Fraud Detection System | Built with Streamlit</p>
    <p>Real-time Bitcoin transaction monitoring and AI-powered threat detection</p>
</div>
""", unsafe_allow_html=True)
