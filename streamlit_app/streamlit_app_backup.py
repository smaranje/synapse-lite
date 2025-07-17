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
import io

# Configuration
USE_DUMMY_DATA = True
BTC_USD_RATE = 65000
st.set_page_config(
    layout="wide",
    page_title="Synapse-Lite Fraud Detector",
    page_icon="🔷",
    initial_sidebar_state="expanded"
)

# Coinbase-inspired CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');

    :root {
        --primary-blue: #1652F0;
        --secondary-blue: #4299E1;
        --background: #FFFFFF;
        --card-bg: #F7FAFC;
        --text-primary: #0A0B0D;
        --text-secondary: #5B616E;
        --border: #E2E8F0;
        --success: #05D168;
        --warning: #F4C430;
        --critical: #FF4747;
    }

    .main, .stApp {
        background: var(--background);
        color: var(--text-primary);
        font-family: 'Montserrat', sans-serif;
        font-size: 16px;
        line-height: 1.5;
    }

    /* Sidebar */
    .css-1d391kg {
        background: var(--card-bg);
        border-right: 1px solid var(--border);
        padding: 1rem;
    }

    .sidebar-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        color: var(--text-secondary);
        text-decoration: none;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .sidebar-item:hover, .sidebar-item.active {
        background: var(--primary-blue);
        color: white;
    }

    /* Header */
    .header {
        padding: 1rem;
        border-bottom: 1px solid var(--border);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .header-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }

    .header-balance {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .header-change {
        font-size: 1rem;
        color: var(--success);
        margin-left: 0.5rem;
    }

    /* Chart Controls */
    .chart-controls {
        display: flex;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }

    .chart-controls button {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.25rem 0.75rem;
        font-size: 0.875rem;
        color: var(--text-secondary);
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .chart-controls button:hover, .chart-controls button.active {
        background: var(--primary-blue);
        color: white;
    }

    /* Quick Actions */
    .quick-actions {
        padding: 1rem;
        border-left: 1px solid var(--border);
        min-width: 200px;
    }

    .quick-action-btn {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        color: var(--primary-blue);
        font-size: 1.2rem;
    }

    .quick-action-btn:hover {
        background: var(--primary-blue);
        color: white;
    }

    /* For You Cards */
    .for-you-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s ease;
    }

    .for-you-card:hover {
        box-shadow: 0 4px 12px rgba(22, 82, 240, 0.1);
    }

    .for-you-icon {
        background: var(--primary-blue);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.2rem;
    }

    .for-you-close {
        cursor: pointer;
        color: var(--text-secondary);
    }

    /* Metric Cards */
    .metric-card {
        background: var(--card-bg);
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(22, 82, 240, 0.1);
        border-color: var(--primary-blue);
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 600;
        color: var(--primary-blue);
        margin: 0.5rem 0;
    }

    .metric-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        font-weight: 500;
    }

    .metric-delta {
        font-size: 0.75rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }

    .metric-delta.positive { color: var(--success); }
    .metric-delta.negative { color: var(--critical); }
    .metric-delta.neutral { color: var(--warning); }

    /* Status Indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.375rem 0.875rem;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 500;
    }

    .status-live { background: var(--success); color: white; }
    .status-warning { background: var(--warning); color: var(--text-primary); }
    .status-critical { background: var(--critical); color: white; }

    /* Alert and Transaction Cards */
    .alert-card, .transaction-card {
        background: var(--card-bg);
        padding: 1.25rem;
        border-radius: 12px;
        border-left: 4px solid var(--primary-blue);
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease;
    }

    .alert-card:hover, .transaction-card:hover {
        transform: translateX(2px);
        box-shadow: 0 4px 16px rgba(22, 82, 240, 0.1);
    }

    .alert-card.critical { border-left-color: var(--critical); }
    .alert-card.high { border-left-color: var(--warning); }
    .alert-card.medium { border-left-color: var(--primary-blue); }
    .alert-card.low { border-left-color: var(--success); }

    /* Inputs and Buttons */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid var(--border);
        padding: 0.75rem;
        font-size: 0.875rem;
        transition: all 0.2s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary-blue);
        box-shadow: 0 0 0 3px rgba(22, 82, 240, 0.1);
    }

    .stSelectbox > div > div > div {
        border-radius: 8px;
        border: 1px solid var(--border);
        font-size: 0.875rem;
    }

    .stButton > button {
        background: var(--primary-blue);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: #0046CC;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(22, 82, 240, 0.2);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--card-bg);
        border-radius: 8px;
        padding: 0.25rem;
        margin-bottom: 1rem;
        border: 1px solid var(--border);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        font-size: 0.875rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
        color: var(--text-secondary);
    }

    .stTabs [aria-selected="true"] {
        background: var(--primary-blue);
        color: white;
    }

    /* Data Tables */
    .stDataFrame {
        background: var(--card-bg);
        border-radius: 12px;
        border: 1px solid var(--border);
        overflow: hidden;
    }

    /* Risk Badges */
    .risk-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }

    .risk-badge.critical { background: var(--critical); color: white; }
    .risk-badge.high { background: var(--warning); color: var(--text-primary); }
    .risk-badge.medium { background: var(--primary-blue); color: white; }
    .risk-badge.low { background: var(--success); color: white; }

    /* Loading Animation */
    .loading-spinner {
        width: 20px;
        height: 20px;
        border: 2px solid var(--border);
        border-top-color: var(--primary-blue);
        border-radius: 50%;
        animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Chart Containers */
    .chart-container {
        background: var(--card-bg);
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }

    /* Pagination */
    .pagination {
        display: flex;
        gap: 0.5rem;
        justify-content: center;
        margin: 1rem 0;
    }

    .pagination button {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
        color: var(--text-primary);
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .pagination button:hover {
        background: var(--primary-blue);
        color: white;
    }

    .pagination button:disabled {
        background: var(--border);
        color: var(--text-secondary);
        cursor: not-allowed;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: var(--text-secondary);
        font-size: 0.85rem;
        border-top: 1px solid var(--border);
        margin-top: 2rem;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .header { flex-direction: column; text-align: center; }
        .quick-actions { display: none; }
        .for-you-card { flex-direction: column; text-align: center; }
    }
    </style>
""", unsafe_allow_html=True)

# Helper Functions
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

@st.cache_data(ttl=5, show_spinner=False)
def generate_dummy_transactions(limit=100):
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

@st.cache_data(ttl=10, show_spinner=False)
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

@st.cache_data(ttl=60, show_spinner=False)
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
    fig_risk = go.Figure()
    fig_risk.add_trace(go.Scatter(
        x=data['hours'],
        y=data['risk_scores'],
        mode='lines',
        line=dict(color='#1652F0', width=2),
        fill='tozeroy',
        fillcolor='rgba(22, 82, 240, 0.1)'
    ))
    fig_risk.update_layout(
        title='',
        xaxis=dict(
            rangeslider=dict(visible=False),
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1H", step="hour", stepmode="backward"),
                    dict(count=1, label="1D", step="day", stepmode="backward"),
                    dict(count=1, label="1W", step="week", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            )
        ),
        yaxis_title='Risk Score (%)',
        template='plotly_white',
        height=300,
        margin=dict(t=20, b=20, l=50, r=50),
        font=dict(family='Montserrat', size=12)
    )
    
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Bar(
        x=data['hours'],
        y=data['transaction_counts'],
        marker=dict(color='#1652F0', opacity=0.8)
    ))
    fig_volume.update_layout(
        title='Transaction Volume (24h)',
        xaxis_title='Time',
        yaxis_title='Transaction Count',
        template='plotly_white',
        height=300,
        font=dict(family='Montserrat', size=12)
    )
    
    alert_data = generate_dummy_alerts(100)
    risk_counts = alert_data['Risk_Level'].value_counts()
    fig_pie = go.Figure(data=[go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        hole=0.4,
        marker=dict(colors=['#FF4747', '#F4C430', '#1652F0', '#05D168'])
    )])
    fig_pie.update_layout(
        title='Alert Distribution by Risk Level',
        template='plotly_white',
        height=300,
        font=dict(family='Montserrat', size=12)
    )
    
    return fig_risk, fig_volume, fig_pie

def paginate_dataframe(df, page_size, page_number):
    start = (page_number - 1) * page_size
    end = start + page_size
    return df.iloc[start:end], len(df)

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-logo"><span style="font-size: 1.5rem; color: var(--primary-blue); font-weight: 600;">🔷 Synapse-Lite</span></div>', unsafe_allow_html=True)
    st.markdown('<p style="color: var(--text-secondary); font-size: 0.85rem;">Fraud Detection System</p>', unsafe_allow_html=True)
    
    pages = {
        "🏠 Dashboard": "Dashboard",
        "💰 Transactions": "Transactions",
        "🚨 Alerts": "Alerts",
        "📊 Analytics": "Analytics",
        "⚙️ Settings": "Settings"
    }
    selected_page = st.radio("", list(pages.keys()), index=0, format_func=lambda x: x, label_visibility="collapsed")
    page_selection = pages[selected_page]
    
    st.markdown("---")
    st.markdown("### System Status")
    st.markdown(create_status_indicator("live", "Monitoring Active"), unsafe_allow_html=True)
    st.markdown(create_status_indicator("warning", "5 Alerts Pending"), unsafe_allow_html=True)
    st.markdown(create_status_indicator("live", "API Connected"), unsafe_allow_html=True)

# Main Content
st.markdown('<div class="header"><div class="header-title">Fraud Detection Overview</div></div>', unsafe_allow_html=True)

if page_selection == "Dashboard":
    # Header Balance and Chart
    total_value = random.uniform(10000, 50000)
    change = random.uniform(-5, 5)
    st.markdown(f"""
    <div style="padding: 1rem;">
        <div class="header-balance">${total_value:,.2f}</div>
        <div class="header-change">↑ ${abs(change):.2f} ({change:+.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)
    
    fig_risk, _, _ = create_advanced_charts()
    st.plotly_chart(fig_risk, use_container_width=True)
    st.markdown('<div class="chart-controls"><button class="active">1H</button><button>1D</button><button>1W</button><button>1M</button><button>1Y</button><button>All</button></div>', unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown('<div class="quick-actions"><h3>Quick Actions</h3>', unsafe_allow_html=True)
    st.markdown('<div class="quick-action-btn">🔍</div><span>Investigate Alert</span>', unsafe_allow_html=True)
    st.markdown('<div class="quick-action-btn">📊</div><span>Generate SAR</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(create_metric_card("Total Transactions", "2,847", "+12% from yesterday", "positive"), unsafe_allow_html=True)
    with col2:
        st.markdown(create_metric_card("Active Alerts", "23", "5 Critical", "negative"), unsafe_allow_html=True)
    with col3:
        st.markdown(create_metric_card("Risk Score", "67.3%", "+2.1% from avg", "neutral"), unsafe_allow_html=True)
    with col4:
        st.markdown(create_metric_card("Detection Rate", "94.2%", "Above target", "positive"), unsafe_allow_html=True)
    
    # For You Section
    st.markdown('<h2>For You</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="for-you-card">
        <div class="for-you-icon">🚨</div>
        <div><strong>Risk Alerts</strong><br>5 critical alerts pending review</div>
        <div class="for-you-close">×</div>
    </div>
    <div class="for-you-card">
        <div class="for-you-icon">💸</div>
        <div><strong>Transaction Summary</strong><br>Review today’s activity</div>
        <div class="for-you-close">×</div>
    </div>
    """, unsafe_allow_html=True)

elif page_selection == "Transactions":
    st.markdown('<div class="header"><div class="header-title">Transaction Monitor</div></div>', unsafe_allow_html=True)
    
    control_col1, control_col2, control_col3 = st.columns([2, 1, 1])
    with control_col1:
        search_term = st.text_input("Search transactions", placeholder="Enter hash, address, or amount")
    with control_col2:
        risk_filter = st.selectbox("Risk Level", ["All", "Critical", "High", "Medium", "Low"])
    with control_col3:
        if st.button("Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    transactions = generate_dummy_transactions(100)
    page_size = 10
    page_number = st.number_input("Page", min_value=1, value=1, step=1)
    paginated_transactions, total_rows = paginate_dataframe(transactions, page_size, page_number)
    
    if not paginated_transactions.empty:
        csv = paginated_transactions.to_csv(index=False)
        st.download_button(
            label="Export as CSV",
            data=csv,
            file_name=f"transactions_page_{page_number}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    for _, tx in paginated_transactions.iterrows():
        risk_level = get_risk_level(tx['ML_Score'], tx['Smurfing_Rule'])
        st.markdown(f"""
        <div class="transaction-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 1.1rem;">{tx['Hash'][:16]}...</div>
                    <div style="color: var(--text-secondary); font-size: 0.9rem; margin: 0.25rem 0;">
                        {tx['NumInputs']} inputs → {tx['NumOutputs']} outputs
                    </div>
                    <div style="color: var(--primary-blue); font-weight: 500;">
                        {tx['TotalOutputValueBTC']:.4f} BTC (${tx['TotalOutputValueBTC'] * BTC_USD_RATE:,.2f})
                    </div>
                </div>
                <div style="text-align: right;">
                    {create_risk_badge(risk_level, tx['ML_Score'])}
                    <div style="color: var(--text-secondary); font-size: 0.8rem; margin-top: 0.5rem;">
                        {tx['Timestamp'].strftime('%H:%M:%S')}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    total_pages = (total_rows + page_size - 1) // page_size
    st.markdown(f"""
    <div class="pagination">
        <button {'disabled' if page_number <= 1 else ''} onclick="window.location.href='?page={page_number-1}'">Previous</button>
        <span>Page {page_number} of {total_pages}</span>
        <button {'disabled' if page_number >= total_pages else ''} onclick="window.location.href='?page={page_number+1}'">Next</button>
    </div>
    """, unsafe_allow_html=True)
    if paginated_transactions.empty:
        st.info("No transactions found matching your criteria.")

elif page_selection == "Alerts":
    st.markdown('<div class="header"><div class="header-title">Security Alerts</div></div>', unsafe_allow_html=True)
    
    alerts = generate_dummy_alerts(50)
    critical_count = len(alerts[alerts['Risk_Level'] == 'Critical'])
    high_count = len(alerts[alerts['Risk_Level'] == 'High'])
    medium_count = len(alerts[alerts['Risk_Level'] == 'Medium'])
    low_count = len(alerts[alerts['Risk_Level'] == 'Low'])
    
    alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)
    with alert_col1:
        st.markdown(create_metric_card("Critical", str(critical_count), "Immediate action", "negative"), unsafe_allow_html=True)
    with alert_col2:
        st.markdown(create_metric_card("High", str(high_count), "Review required", "neutral"), unsafe_allow_html=True)
    with alert_col3:
        st.markdown(create_metric_card("Medium", str(medium_count), "Monitor closely", "neutral"), unsafe_allow_html=True)
    with alert_col4:
        st.markdown(create_metric_card("Low", str(low_count), "Standard review", "positive"), unsafe_allow_html=True)
    
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
    with filter_col1:
        alert_search = st.text_input("Search alerts", placeholder="Enter transaction hash or details")
    with filter_col2:
        severity_filter = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])
    with filter_col3:
        if st.button("Refresh Alerts", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    if not alerts.empty:
        csv = alerts.to_csv(index=False)
        st.download_button(
            label="Export Alerts as CSV",
            data=csv,
            file_name="alerts.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    page_size = 10
    page_number = st.number_input("Page", min_value=1, value=1, step=1, key="alerts_page")
    paginated_alerts, total_rows = paginate_dataframe(alerts, page_size, page_number)
    
    if not paginated_alerts.empty:
        if severity_filter != "All":
            paginated_alerts = paginated_alerts[paginated_alerts['Risk_Level'] == severity_filter]
        if alert_search:
            paginated_alerts = paginated_alerts[paginated_alerts['Hash'].str.contains(alert_search, case=False, na=False)]
        
        paginated_alerts = paginated_alerts.sort_values(['Risk_Level', 'Timestamp'], ascending=[True, False])
        
        for _, alert in paginated_alerts.iterrows():
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
                        <div style="color: var(--text-secondary); margin-bottom: 0.75rem;">
                            {description}
                        </div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem;">
                            <strong>Transaction:</strong> {alert['Hash'][:16]}...<br>
                            <strong>Amount:</strong> {alert['TotalOutputValue']/1e8:.4f} BTC<br>
                            <strong>Time:</strong> {alert['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <button style="background: var(--primary-blue); color: white; border: none; border-radius: 8px; padding: 0.625rem 1rem; font-size: 0.875rem; cursor: pointer; font-weight: 500; margin-bottom: 0.5rem;">
                            Investigate
                        </button>
                        <br>
                        <button style="background: var(--success); color: white; border: none; border-radius: 8px; padding: 0.625rem 1rem; font-size: 0.875rem; cursor: pointer; font-weight: 500;">
                            Generate SAR
                        </button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        total_pages = (total_rows + page_size - 1) // page_size
        st.markdown(f"""
        <div class="pagination">
            <button {'disabled' if page_number <= 1 else ''} onclick="window.location.href='?page={page_number-1}'">Previous</button>
            <span>Page {page_number} of {total_pages}</span>
            <button {'disabled' if page_number >= total_pages else ''} onclick="window.location.href='?page={page_number+1}'">Next</button>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No alerts found matching your criteria.")

elif page_selection == "Analytics":
    st.markdown('<div class="header"><div class="header-title">Fraud Analytics</div></div>', unsafe_allow_html=True)
    
    chart_tabs = st.tabs(["Risk Trends", "Transaction Volume", "Alert Distribution", "Pattern Analysis"])
    fig_risk, fig_volume, fig_pie = create_advanced_charts()
    
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
            <div class="chart-container">
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
            <div class="chart-container">
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
            <div class="chart-container">
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
            <div class="chart-container">
                <p><strong>Peak Alert Hour:</strong> {peak_alert_hour:02d}:00</p>
                <p><strong>Alerts at Peak:</strong> {hourly_alerts.max()}</p>
                <p><strong>Quietest Hour:</strong> {hourly_alerts.idxmin():02d}:00</p>
            </div>
            """, unsafe_allow_html=True)
    
    with chart_tabs[3]:
        st.markdown("### Pattern Analysis")
        transactions = generate_dummy_transactions(100)
        fig_ml = px.histogram(
            transactions,
            x='ML_Score',
            nbins=20,
            title='ML Score Distribution',
            color_discrete_sequence=['#1652F0']
        )
        fig_ml.update_layout(template='plotly_white', font=dict(family='Montserrat', size=12))
        st.plotly_chart(fig_ml, use_container_width=True)
        
        fig_scatter = px.scatter(
            transactions,
            x='TotalOutputValueBTC',
            y='ML_Score',
            color='Risk_Level',
            size='NumOutputs',
            title='Transaction Amount vs Risk Score',
            color_discrete_map={'Critical': '#FF4747', 'High': '#F4C430', 'Medium': '#1652F0', 'Low': '#05D168'}
        )
        fig_scatter.update_layout(template='plotly_white', font=dict(family='Montserrat', size=12))
        st.plotly_chart(fig_scatter, use_container_width=True)

elif page_selection == "Settings":
    st.markdown('<div class="header"><div class="header-title">Settings</div></div>', unsafe_allow_html=True)
    
    settings_tabs = st.tabs(["General", "Security", "Monitoring", "Integrations"])
    with settings_tabs[0]:
        st.markdown("## General Settings")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Display Preferences")
            st.selectbox("Theme", ["Light", "Dark", "Auto"], key="theme")
            st.slider("Refresh Rate (seconds)", 1, 60, 5, key="refresh_rate")
            st.checkbox("Show animations", value=True, key="animations")
            st.checkbox("Enable notifications", value=True, key="notifications")
        with col2:
            st.markdown("### Data Settings")
            st.selectbox("Data Source", ["Demo Data", "Live Feed", "Historical"], key="data_source")
            st.slider("Transaction Limit", 10, 1000, 100, key="tx_limit")
            st.slider("Alert History (days)", 1, 30, 7, key="alert_history")
    
    with settings_tabs[1]:
        st.markdown("## Security Settings")
        st.markdown("### API Configuration")
        st.text_input("Gemini API Key", type="password", value="••••••••••••••••", key="api_key")
        st.text_input("Neo4j Connection", value="bolt://neo4j:7687", key="neo4j_connection")
        st.markdown("### Access Control")
        st.checkbox("Enable audit logging", value=True, key="audit_logging")
        st.checkbox("Require 2FA", value=False, key="2fa")
        st.selectbox("Session timeout", ["15 min", "30 min", "1 hour", "4 hours"], key="session_timeout")
    
    with settings_tabs[2]:
        st.markdown("## Monitoring Settings")
        st.markdown("### Alert Thresholds")
        st.slider("Critical Risk Threshold", 0.0, 1.0, 0.9, key="critical_threshold")
        st.slider("High Risk Threshold", 0.0, 1.0, 0.7, key="high_threshold")
        st.slider("Medium Risk Threshold", 0.0, 1.0, 0.4, key="medium_threshold")
        st.markdown("### Notification Settings")
        st.checkbox("Email alerts for critical risks", value=True, key="email_alerts")
        st.checkbox("SMS alerts for system issues", value=False, key="sms_alerts")
        st.text_input("Alert email", value="admin@example.com", key="alert_email")
    
    with settings_tabs[3]:
        st.markdown("## Integration Settings")
        st.markdown("### External Services")
        st.text_input("Webhook URL", placeholder="https://your-webhook.com/alerts", key="webhook")
        st.selectbox("Export Format", ["JSON", "CSV", "XML"], key="export_format")
        st.checkbox("Enable blockchain explorer links", value=True, key="blockchain_links")
        st.markdown("### Database Settings")
        st.text_input("Backup Location", value="/backups/", key="backup_location")
        st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"], key="backup_frequency")

# Footer
st.markdown("""
<div class="footer">
    <p>Synapse-Lite Fraud Detection System | Built with Streamlit</p>
    <p>© 2025 xAI. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
