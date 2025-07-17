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
import requests

# Configuration
USE_DUMMY_DATA = True
BTC_USD_RATE = 65000
st.set_page_config(
    layout="wide", 
    page_title="Synapse-Lite Fraud Detector",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# Professional CSS with Montserrat font and clean design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
        color: #e0e0e0;
        font-family: 'Montserrat', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
    }
    
    /* Header styling */
    h1 {
        color: #ffffff;
        font-weight: 700;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        font-family: 'Montserrat', sans-serif;
    }
    
    h2, h3 {
        color: #f0f0f0;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-family: 'Montserrat', sans-serif;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #16213e 0%, #0f3460 100%);
        border-right: 1px solid #2d3748;
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: #e2e8f0;
    }
    
    /* Custom metric cards */
    .metric-card {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #4a5568;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        border-color: #63b3ed;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #63b3ed;
        margin: 0.5rem 0;
        font-family: 'Montserrat', sans-serif;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #a0aec0;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-family: 'Montserrat', sans-serif;
    }
    
    .metric-delta {
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
        font-family: 'Montserrat', sans-serif;
    }
    
    .metric-delta.positive {
        color: #48bb78;
    }
    
    .metric-delta.negative {
        color: #f56565;
    }
    
    .metric-delta.neutral {
        color: #ed8936;
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
        letter-spacing: 0.5px;
        font-family: 'Montserrat', sans-serif;
    }
    
    .status-live {
        background: linear-gradient(135deg, #48bb78, #38a169);
        color: white;
        animation: pulse 2s infinite;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #ed8936, #dd6b20);
        color: white;
    }
    
    .status-critical {
        background: linear-gradient(135deg, #f56565, #e53e3e);
        color: white;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Enhanced alert cards */
    .alert-card {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid #63b3ed;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .alert-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }
    
    .alert-card.critical {
        border-left-color: #f56565;
        background: linear-gradient(135deg, #2d1b1b 0%, #1a1010 100%);
    }
    
    .alert-card.high {
        border-left-color: #ed8936;
        background: linear-gradient(135deg, #2d2318 0%, #1a1710 100%);
    }
    
    .alert-card.medium {
        border-left-color: #4299e1;
        background: linear-gradient(135deg, #1a2332 0%, #0f1419 100%);
    }
    
    .alert-card.low {
        border-left-color: #48bb78;
        background: linear-gradient(135deg, #1a2e1a 0%, #0f1a0f 100%);
    }
    
    /* Transaction cards */
    .transaction-card {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid #4a5568;
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .transaction-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #63b3ed, #4299e1);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .transaction-card:hover::before {
        transform: scaleX(1);
    }
    
    .transaction-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        border-color: #63b3ed;
    }
    
    /* Enhanced buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3);
        font-family: 'Montserrat', sans-serif;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(66, 153, 225, 0.4);
    }
    
    /* Data tables */
    .stDataFrame {
        background: rgba(45, 55, 72, 0.5);
        border-radius: 15px;
        border: 1px solid #4a5568;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    /* Risk score badges */
    .risk-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-family: 'Montserrat', sans-serif;
    }
    
    .risk-badge.critical {
        background: linear-gradient(135deg, #f56565, #e53e3e);
        color: white;
    }
    
    .risk-badge.high {
        background: linear-gradient(135deg, #ed8936, #dd6b20);
        color: white;
    }
    
    .risk-badge.medium {
        background: linear-gradient(135deg, #4299e1, #3182ce);
        color: white;
    }
    
    .risk-badge.low {
        background: linear-gradient(135deg, #48bb78, #38a169);
        color: white;
    }
    
    /* Chat interface */
    .chat-container {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        border-radius: 15px;
        border: 1px solid #4a5568;
        padding: 1rem;
        margin-bottom: 1rem;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .chat-message {
        margin-bottom: 1rem;
        padding: 0.75rem;
        border-radius: 10px;
        font-family: 'Montserrat', sans-serif;
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, #4299e1, #3182ce);
        color: white;
        margin-left: 2rem;
    }
    
    .chat-message.assistant {
        background: linear-gradient(135deg, #2d3748, #1a202c);
        color: #e0e0e0;
        border: 1px solid #4a5568;
        margin-right: 2rem;
    }
    
    .chat-input {
        background: #2d3748;
        border: 1px solid #4a5568;
        border-radius: 10px;
        padding: 0.75rem;
        color: #e0e0e0;
        font-family: 'Montserrat', sans-serif;
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    .chat-input:focus {
        outline: none;
        border-color: #63b3ed;
    }
    
    /* Chart containers */
    .chart-container {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #4a5568;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Professional navigation */
    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 10px;
        color: #e2e8f0;
        text-decoration: none;
        transition: all 0.3s ease;
        cursor: pointer;
        font-family: 'Montserrat', sans-serif;
        font-weight: 500;
    }
    
    .nav-item:hover {
        background: rgba(66, 153, 225, 0.1);
        color: #63b3ed;
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #4299e1, #3182ce);
        color: white;
    }
    
    /* Professional text styling */
    .professional-text {
        font-family: 'Montserrat', sans-serif;
        font-weight: 400;
        line-height: 1.6;
    }
    
    .professional-heading {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        color: #ffffff;
    }
    
    .professional-subheading {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        color: #f0f0f0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #718096;
        font-size: 0.9rem;
        border-top: 1px solid #2d3748;
        margin-top: 3rem;
        font-family: 'Montserrat', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Helper Functions
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

def create_metric_card(label, value, delta=None, delta_type="neutral"):
    """Create a beautiful metric card"""
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
    """Create a status indicator badge"""
    return f'<span class="status-indicator status-{status}">{text}</span>'

def create_risk_badge(risk_level, score=None):
    """Create a risk level badge"""
    score_text = f" ({int(score*100)}%)" if score else ""
    return f'<span class="risk-badge {risk_level.lower()}">{risk_level}{score_text}</span>'

def generate_sar_with_gemini(transaction_data, user_query=""):
    """Generate SAR using Gemini API"""
    try:
        # Prepare transaction context
        context = f"""
        Transaction Hash: {transaction_data.get('hash', 'N/A')}
        Amount: {transaction_data.get('amount_btc', 0):.4f} BTC (${transaction_data.get('amount_usd', 0):,.2f})
        Risk Score: {transaction_data.get('risk_score', 0):.2f}
        Timestamp: {transaction_data.get('timestamp', 'N/A')}
        Inputs: {transaction_data.get('inputs', 0)}
        Outputs: {transaction_data.get('outputs', 0)}
        Smurfing Rule Triggered: {transaction_data.get('smurfing', False)}
        """
        
        # Call Flask LLM service
        response = requests.post(
            "http://flask-llm-service:5000/generate-sar",
            json={
                "transaction_hash": transaction_data.get('hash', ''),
                "ml_fraud_score": transaction_data.get('risk_score', 0),
                "is_smurfing_rule": transaction_data.get('smurfing', False),
                "total_input_value": transaction_data.get('amount_btc', 0) * 1e8,
                "total_output_value": transaction_data.get('amount_btc', 0) * 1e8,
                "num_inputs": transaction_data.get('inputs', 1),
                "num_outputs": transaction_data.get('outputs', 1),
                "context": user_query if user_query else "Generate a comprehensive SAR report for this suspicious transaction."
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get('sar_draft', 'Failed to generate SAR')
        else:
            return f"Error generating SAR: {response.status_code}"
            
    except Exception as e:
        return f"Error connecting to AI service: {str(e)}"

def chat_with_gemini(user_message, context=""):
    """Chat with Gemini for general fraud analysis queries"""
    try:
        response = requests.post(
            "http://flask-llm-service:5000/generate-sar",
            json={
                "transaction_hash": "CHAT_QUERY",
                "ml_fraud_score": 0.0,
                "is_smurfing_rule": False,
                "total_input_value": 0,
                "total_output_value": 0,
                "num_inputs": 0,
                "num_outputs": 0,
                "context": f"User query: {user_message}\n\nContext: {context}\n\nPlease provide a helpful response about fraud detection, compliance, or SAR reporting."
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get('sar_draft', 'I apologize, but I cannot process your request at the moment.')
        else:
            return "I'm experiencing technical difficulties. Please try again later."
            
    except Exception as e:
        return "I'm currently unable to connect to the AI service. Please check your connection and try again."

@st.cache_data(ttl=5)
def generate_dummy_transactions(limit=10):
    """Generate dummy transaction data."""
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
    """Generate dummy alert data."""
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
    """Generate analytics data for charts."""
    current_time = datetime.now()
    
    # Time series data
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
    """Create advanced interactive charts."""
    data = generate_analytics_data()
    
    # Risk Score Trend Chart
    fig_risk = go.Figure()
    fig_risk.add_trace(go.Scatter(
        x=data['hours'],
        y=data['risk_scores'],
        mode='lines+markers',
        name='Risk Score',
        line=dict(color='#4299e1', width=3),
        marker=dict(size=8, color='#63b3ed'),
        fill='tonexty',
        fillcolor='rgba(66, 153, 225, 0.1)'
    ))
    fig_risk.update_layout(
        title='Risk Score Trend (24h)',
        xaxis_title='Time',
        yaxis_title='Risk Score',
        template='plotly_dark',
        height=400,
        showlegend=False,
        font=dict(family="Montserrat, sans-serif")
    )
    
    # Transaction Volume Chart
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Bar(
        x=data['hours'],
        y=data['transaction_counts'],
        name='Transactions',
        marker=dict(color='#48bb78', opacity=0.8)
    ))
    fig_volume.update_layout(
        title='Transaction Volume (24h)',
        xaxis_title='Time',
        yaxis_title='Transaction Count',
        template='plotly_dark',
        height=400,
        showlegend=False,
        font=dict(family="Montserrat, sans-serif")
    )
    
    # Alert Distribution Pie Chart
    alert_data = generate_dummy_alerts(100)
    risk_counts = alert_data['Risk_Level'].value_counts()
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        hole=0.4,
        marker=dict(colors=['#f56565', '#ed8936', '#4299e1', '#48bb78'])
    )])
    fig_pie.update_layout(
        title='Alert Distribution by Risk Level',
        template='plotly_dark',
        height=400,
        font=dict(family="Montserrat, sans-serif")
    )
    
    return fig_risk, fig_volume, fig_pie

# Initialize session state for chat
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'selected_transaction' not in st.session_state:
    st.session_state.selected_transaction = None

# Enhanced Sidebar with AI Chat
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 1.5rem; margin: 0; color: #63b3ed; font-family: 'Montserrat', sans-serif;">SYNAPSE-LITE</h1>
        <p style="color: #a0aec0; font-size: 0.9rem; margin: 0.5rem 0; font-family: 'Montserrat', sans-serif;">Fraud Detection System</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation without icons
    pages = {
        "Dashboard": "Dashboard",
        "Transactions": "Transactions", 
        "Alerts": "Alerts",
        "Analytics": "Analytics",
        "Settings": "Settings"
    }
    
    selected_page = st.radio("", list(pages.keys()), index=0)
    page_selection = pages[selected_page]
    
    st.markdown("---")
    
    # AI Chat Interface
    st.markdown("### AI Assistant")
    st.markdown('<p class="professional-text">Ask about fraud patterns, compliance, or generate SAR reports</p>', unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for i, (role, message) in enumerate(st.session_state.chat_history[-5:]):  # Show last 5 messages
            st.markdown(f'<div class="chat-message {role}">{message}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Type your message...", key="chat_input", placeholder="e.g., Generate SAR for high-risk transaction")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Send", use_container_width=True):
            if user_input:
                st.session_state.chat_history.append(("user", user_input))
                
                # Generate AI response
                with st.spinner("AI is thinking..."):
                    if "sar" in user_input.lower() and st.session_state.selected_transaction:
                        response = generate_sar_with_gemini(st.session_state.selected_transaction, user_input)
                    else:
                        response = chat_with_gemini(user_input)
                
                st.session_state.chat_history.append(("assistant", response))
                st.rerun()
    
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    st.markdown("---")
    
    # System Status
    st.markdown("### System Status")
    st.markdown(create_status_indicator("live", "Monitoring Active"), unsafe_allow_html=True)
    st.markdown(create_status_indicator("warning", "5 Alerts Pending"), unsafe_allow_html=True)
    st.markdown(create_status_indicator("live", "AI Connected"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### Quick Stats")
    metrics = {
        "transactions_today": random.randint(1000, 5000),
        "alerts_today": random.randint(10, 50),
        "risk_score": random.uniform(50, 80)
    }
    
    st.markdown(f"""
    <div style="font-size: 0.9rem; color: #a0aec0; font-family: 'Montserrat', sans-serif;">
        <p>Transactions Today: <strong style="color: #63b3ed;">{metrics['transactions_today']}</strong></p>
        <p>Alerts Today: <strong style="color: #ed8936;">{metrics['alerts_today']}</strong></p>
        <p>Avg Risk Score: <strong style="color: #48bb78;">{metrics['risk_score']:.1f}%</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; font-size: 0.8rem; font-family: 'Montserrat', sans-serif;">
        <p>© 2024 Synapse-Lite<br>Fraud Detection System</p>
    </div>
    """, unsafe_allow_html=True)

# Main Content
if page_selection == "Dashboard":
    st.markdown('<h1 class="professional-heading">FRAUD DETECTION DASHBOARD</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="professional-subheading">Real-time Bitcoin transaction monitoring and threat analysis</h3>', unsafe_allow_html=True)
    
    # Status indicator
    st.markdown(create_status_indicator("live", "Live Monitoring Active"), unsafe_allow_html=True)
    st.markdown("---")
    
    # Enhanced metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Total Transactions", 
            "2,847", 
            "+12% from yesterday", 
            "positive"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Active Alerts", 
            "23", 
            "5 Critical", 
            "negative"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Risk Score", 
            "67.3%", 
            "+2.1% from avg", 
            "neutral"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Detection Rate", 
            "94.2%", 
            "Above target", 
            "positive"
        ), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts section
    st.markdown('<h2 class="professional-subheading">Real-time Analytics</h2>', unsafe_allow_html=True)
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        fig_risk, fig_volume, fig_pie = create_advanced_charts()
        st.plotly_chart(fig_risk, use_container_width=True)
    
    with chart_col2:
        st.plotly_chart(fig_volume, use_container_width=True)
    
    # Alert distribution
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    # Recent transactions and alerts
    recent_col1, recent_col2 = st.columns(2)
    
    with recent_col1:
        st.markdown('<h2 class="professional-subheading">Recent Transactions</h2>', unsafe_allow_html=True)
        transactions = generate_dummy_transactions(5)
        
        for _, tx in transactions.iterrows():
            risk_level = get_risk_level(tx['ML_Score'], tx['Smurfing_Rule'])
            tx_data = {
                'hash': tx['Hash'],
                'amount_btc': tx['TotalOutputValueBTC'],
                'amount_usd': tx['TotalOutputValueBTC'] * BTC_USD_RATE,
                'risk_score': tx['ML_Score'],
                'timestamp': tx['Timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'inputs': tx['NumInputs'],
                'outputs': tx['NumOutputs'],
                'smurfing': tx['Smurfing_Rule']
            }
            
            if st.button(f"Select {tx['Hash'][:12]}...", key=f"select_tx_{tx['Hash'][:8]}"):
                st.session_state.selected_transaction = tx_data
                st.success("Transaction selected for AI analysis")
            
            st.markdown(f"""
            <div class="transaction-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-family: 'Montserrat', sans-serif;">{tx['Hash'][:12]}...</strong>
                        <br>
                        <small style="color: #a0aec0; font-family: 'Montserrat', sans-serif;">{tx['TotalOutputValueBTC']:.4f} BTC</small>
                    </div>
                    <div>
                        {create_risk_badge(risk_level, tx['ML_Score'])}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with recent_col2:
        st.markdown('<h2 class="professional-subheading">Recent Alerts</h2>', unsafe_allow_html=True)
        alerts = generate_dummy_alerts(5)
        
        for _, alert in alerts.iterrows():
            risk_level = alert['Risk_Level']
            alert_data = {
                'hash': alert['Hash'],
                'amount_btc': alert['TotalOutputValue'] / 1e8,
                'amount_usd': (alert['TotalOutputValue'] / 1e8) * BTC_USD_RATE,
                'risk_score': alert['ML_Score'],
                'timestamp': alert['Timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'inputs': random.randint(1, 5),
                'outputs': random.randint(1, 5),
                'smurfing': alert['Smurfing_Rule']
            }
            
            if st.button(f"Generate SAR {alert['Hash'][:8]}...", key=f"sar_alert_{alert['Hash'][:8]}"):
                st.session_state.selected_transaction = alert_data
                with st.spinner("Generating SAR with AI..."):
                    sar_response = generate_sar_with_gemini(alert_data, "Generate a comprehensive SAR report for this suspicious transaction")
                st.session_state.chat_history.append(("assistant", f"SAR Report for {alert['Hash'][:12]}...\n\n{sar_response}"))
                st.success("SAR generated! Check AI Assistant.")
            
            st.markdown(f"""
            <div class="alert-card {risk_level.lower()}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-family: 'Montserrat', sans-serif;">{alert['Hash'][:12]}...</strong>
                        <br>
                        <small style="color: #a0aec0; font-family: 'Montserrat', sans-serif;">{alert['Timestamp'].strftime('%H:%M:%S')}</small>
                    </div>
                    <div>
                        {create_risk_badge(risk_level, alert['ML_Score'])}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif page_selection == "Transactions":
    st.markdown('<h1 class="professional-heading">TRANSACTION MONITOR</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="professional-subheading">Real-time Bitcoin transaction analysis</h3>', unsafe_allow_html=True)
    
    # Controls
    control_col1, control_col2, control_col3 = st.columns([2, 1, 1])
    
    with control_col1:
        search_term = st.text_input("Search transactions...", placeholder="Enter hash, address, or amount")
    
    with control_col2:
        risk_filter = st.selectbox("Risk Level", ["All", "Critical", "High", "Medium", "Low"])
    
    with control_col3:
        if st.button("Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Transaction table
    transactions = generate_dummy_transactions(20)
    
    if not transactions.empty:
        # Apply filters
        if risk_filter != "All":
            transactions = transactions[transactions['Risk_Level'] == risk_filter]
        
        if search_term:
            transactions = transactions[
                transactions['Hash'].str.contains(search_term, case=False, na=False)
            ]
        
        # Display transactions
        for _, tx in transactions.iterrows():
            risk_level = get_risk_level(tx['ML_Score'], tx['Smurfing_Rule'])
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="transaction-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; font-size: 1.1rem; font-family: 'Montserrat', sans-serif;">{tx['Hash'][:16]}...</div>
                            <div style="color: #a0aec0; font-size: 0.9rem; margin: 0.25rem 0; font-family: 'Montserrat', sans-serif;">
                                {tx['NumInputs']} inputs → {tx['NumOutputs']} outputs
                            </div>
                            <div style="color: #63b3ed; font-weight: 500; font-family: 'Montserrat', sans-serif;">
                                {tx['TotalOutputValueBTC']:.4f} BTC (${tx['TotalOutputValueBTC'] * BTC_USD_RATE:,.2f})
                            </div>
                        </div>
                        <div style="text-align: right;">
                            {create_risk_badge(risk_level, tx['ML_Score'])}
                            <div style="color: #a0aec0; font-size: 0.8rem; margin-top: 0.5rem; font-family: 'Montserrat', sans-serif;">
                                {tx['Timestamp'].strftime('%H:%M:%S')}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                tx_data = {
                    'hash': tx['Hash'],
                    'amount_btc': tx['TotalOutputValueBTC'],
                    'amount_usd': tx['TotalOutputValueBTC'] * BTC_USD_RATE,
                    'risk_score': tx['ML_Score'],
                    'timestamp': tx['Timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'inputs': tx['NumInputs'],
                    'outputs': tx['NumOutputs'],
                    'smurfing': tx['Smurfing_Rule']
                }
                
                if st.button("Analyze", key=f"analyze_{tx['Hash'][:8]}", use_container_width=True):
                    st.session_state.selected_transaction = tx_data
                    st.success("Transaction selected for AI analysis")
    else:
        st.info("No transactions found matching your criteria.")

elif page_selection == "Alerts":
    st.markdown('<h1 class="professional-heading">SECURITY ALERTS</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="professional-subheading">Monitor and investigate suspicious activity</h3>', unsafe_allow_html=True)
    
    # Alert summary metrics
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
    
    # Alert filters
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
    
    with filter_col1:
        alert_search = st.text_input("Search alerts...", placeholder="Enter transaction hash or details")
    
    with filter_col2:
        severity_filter = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])
    
    with filter_col3:
        if st.button("Refresh Alerts", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Alert list
    if not alerts.empty:
        # Apply filters
        if severity_filter != "All":
            alerts = alerts[alerts['Risk_Level'] == severity_filter]
        
        if alert_search:
            alerts = alerts[alerts['Hash'].str.contains(alert_search, case=False, na=False)]
        
        # Sort by risk level and timestamp
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
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="alert-card {risk_level.lower()}">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem; font-family: 'Montserrat', sans-serif;">
                                {create_risk_badge(risk_level)} Alert {alert['Hash'][:8]}...
                            </div>
                            <div style="color: #e2e8f0; margin-bottom: 0.75rem; font-family: 'Montserrat', sans-serif;">
                                {description}
                            </div>
                            <div style="color: #a0aec0; font-size: 0.9rem; font-family: 'Montserrat', sans-serif;">
                                <strong>Transaction:</strong> {alert['Hash'][:16]}...<br>
                                <strong>Amount:</strong> {alert['TotalOutputValue']/1e8:.4f} BTC<br>
                                <strong>Time:</strong> {alert['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                alert_data = {
                    'hash': alert['Hash'],
                    'amount_btc': alert['TotalOutputValue'] / 1e8,
                    'amount_usd': (alert['TotalOutputValue'] / 1e8) * BTC_USD_RATE,
                    'risk_score': alert['ML_Score'],
                    'timestamp': alert['Timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'inputs': random.randint(1, 5),
                    'outputs': random.randint(1, 5),
                    'smurfing': alert['Smurfing_Rule']
                }
                
                if st.button("Generate SAR", key=f"sar_{alert['Hash'][:8]}", use_container_width=True):
                    st.session_state.selected_transaction = alert_data
                    with st.spinner("Generating SAR with AI..."):
                        sar_response = generate_sar_with_gemini(alert_data, "Generate a comprehensive SAR report for this suspicious transaction")
                    st.session_state.chat_history.append(("assistant", f"SAR Report for {alert['Hash'][:12]}...\n\n{sar_response}"))
                    st.success("SAR generated! Check AI Assistant.")
    else:
        st.info("No alerts found matching your criteria.")

elif page_selection == "Analytics":
    st.markdown('<h1 class="professional-heading">FRAUD ANALYTICS</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="professional-subheading">Deep dive into fraud trends and patterns</h3>', unsafe_allow_html=True)
    
    # Create comprehensive analytics
    fig_risk, fig_volume, fig_pie = create_advanced_charts()
    
    # Advanced charts
    chart_tabs = st.tabs(["Risk Trends", "Transaction Volume", "Alert Distribution", "Pattern Analysis"])
    
    with chart_tabs[0]:
        st.plotly_chart(fig_risk, use_container_width=True)
        
        # Additional risk metrics
        risk_col1, risk_col2 = st.columns(2)
        
        with risk_col1:
            st.markdown('<h3 class="professional-subheading">Risk Score Statistics</h3>', unsafe_allow_html=True)
            data = generate_analytics_data()
            avg_risk = np.mean(data['risk_scores'])
            max_risk = np.max(data['risk_scores'])
            min_risk = np.min(data['risk_scores'])
            
            st.markdown(f"""
            <div class="chart-container">
                <p style="font-family: 'Montserrat', sans-serif;"><strong>Average Risk Score:</strong> {avg_risk:.1f}%</p>
                <p style="font-family: 'Montserrat', sans-serif;"><strong>Peak Risk Score:</strong> {max_risk:.1f}%</p>
                <p style="font-family: 'Montserrat', sans-serif;"><strong>Lowest Risk Score:</strong> {min_risk:.1f}%</p>
                <p style="font-family: 'Montserrat', sans-serif;"><strong>Risk Volatility:</strong> {np.std(data['risk_scores']):.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with risk_col2:
            st.markdown('<h3 class="professional-subheading">Risk Level Distribution</h3>', unsafe_allow_html=True)
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
        
        # Transaction insights
        st.markdown('<h3 class="professional-subheading">Transaction Insights</h3>', unsafe_allow_html=True)
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
        
        # Alert analysis
        st.markdown('<h3 class="professional-subheading">Alert Analysis</h3>', unsafe_allow_html=True)
        alerts = generate_dummy_alerts(100)
        
        analysis_col1, analysis_col2 = st.columns(2)
        
        with analysis_col1:
            st.markdown('<h4 class="professional-subheading">Alert Triggers</h4>', unsafe_allow_html=True)
            smurfing_alerts = len(alerts[alerts['Smurfing_Rule'] == True])
            ml_alerts = len(alerts[alerts['ML_Score'] >= 0.9])
            
            st.markdown(f"""
            <div class="chart-container">
                <p style="font-family: 'Montserrat', sans-serif;"><strong>Smurfing Rule Triggers:</strong> {smurfing_alerts}</p>
                <p style="font-family: 'Montserrat', sans-serif;"><strong>High ML Score Alerts:</strong> {ml_alerts}</p>
                <p style="font-family: 'Montserrat', sans-serif;"><strong>Combined Triggers:</strong> {len(alerts[(alerts['Smurfing_Rule'] == True) & (alerts['ML_Score'] >= 0.9)])}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with analysis_col2:
            st.markdown('<h4 class="professional-subheading">Alert Timing</h4>', unsafe_allow_html=True)
            hourly_alerts = alerts.groupby(alerts['Timestamp'].dt.hour).size()
            peak_alert_hour = hourly_alerts.idxmax()
            
            st.markdown(f"""
            <div class="chart-container">
                <p style="font-family: 'Montserrat', sans-serif;"><strong>Peak Alert Hour:</strong> {peak_alert_hour:02d}:00</p>
                <p style="font-family: 'Montserrat', sans-serif;"><strong>Alerts at Peak:</strong> {hourly_alerts.max()}</p>
                <p style="font-family: 'Montserrat', sans-serif;"><strong>Quietest Hour:</strong> {hourly_alerts.idxmin():02d}:00</p>
            </div>
            """, unsafe_allow_html=True)
    
    with chart_tabs[3]:
        st.markdown('<h3 class="professional-subheading">Pattern Analysis</h3>', unsafe_allow_html=True)
        
        # Create pattern analysis charts
        transactions = generate_dummy_transactions(100)
        
        # ML Score distribution
        fig_ml = px.histogram(
            transactions, 
            x='ML_Score', 
            nbins=20, 
            title='ML Score Distribution',
            color_discrete_sequence=['#4299e1']
        )
        fig_ml.update_layout(template='plotly_dark', font=dict(family="Montserrat, sans-serif"))
        st.plotly_chart(fig_ml, use_container_width=True)
        
        # Transaction size vs risk
        fig_scatter = px.scatter(
            transactions,
            x='TotalOutputValueBTC',
            y='ML_Score',
            color='Risk_Level',
            size='NumOutputs',
            title='Transaction Amount vs Risk Score',
            color_discrete_map={
                'Critical': '#f56565',
                'High': '#ed8936', 
                'Medium': '#4299e1',
                'Low': '#48bb78'
            }
        )
        fig_scatter.update_layout(template='plotly_dark', font=dict(family="Montserrat, sans-serif"))
        st.plotly_chart(fig_scatter, use_container_width=True)

elif page_selection == "Settings":
    st.markdown('<h1 class="professional-heading">SETTINGS</h1>', unsafe_allow_html=True)
    st.markdown('<h3 class="professional-subheading">Configure system parameters and preferences</h3>', unsafe_allow_html=True)
    
    # Settings tabs
    settings_tabs = st.tabs(["General", "Security", "Monitoring", "Integrations"])
    
    with settings_tabs[0]:
        st.markdown('<h2 class="professional-subheading">General Settings</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h3 class="professional-subheading">Display Preferences</h3>', unsafe_allow_html=True)
            st.selectbox("Theme", ["Dark", "Light", "Auto"])
            st.slider("Refresh Rate (seconds)", 1, 60, 5)
            st.checkbox("Show animations", value=True)
            st.checkbox("Enable notifications", value=True)
        
        with col2:
            st.markdown('<h3 class="professional-subheading">Data Settings</h3>', unsafe_allow_html=True)
            st.selectbox("Data Source", ["Demo Data", "Live Feed", "Historical"])
            st.slider("Transaction Limit", 10, 1000, 100)
            st.slider("Alert History (days)", 1, 30, 7)
    
    with settings_tabs[1]:
        st.markdown('<h2 class="professional-subheading">Security Settings</h2>', unsafe_allow_html=True)
        
        st.markdown('<h3 class="professional-subheading">API Configuration</h3>', unsafe_allow_html=True)
        st.text_input("Gemini API Key", type="password", value="••••••••••••••••")
        st.text_input("Neo4j Connection", value="bolt://neo4j:7687")
        
        st.markdown('<h3 class="professional-subheading">Access Control</h3>', unsafe_allow_html=True)
        st.checkbox("Enable audit logging", value=True)
        st.checkbox("Require 2FA", value=False)
        st.selectbox("Session timeout", ["15 min", "30 min", "1 hour", "4 hours"])
    
    with settings_tabs[2]:
        st.markdown('<h2 class="professional-subheading">Monitoring Settings</h2>', unsafe_allow_html=True)
        
        st.markdown('<h3 class="professional-subheading">Alert Thresholds</h3>', unsafe_allow_html=True)
        st.slider("Critical Risk Threshold", 0.0, 1.0, 0.9)
        st.slider("High Risk Threshold", 0.0, 1.0, 0.7)
        st.slider("Medium Risk Threshold", 0.0, 1.0, 0.4)
        
        st.markdown('<h3 class="professional-subheading">Notification Settings</h3>', unsafe_allow_html=True)
        st.checkbox("Email alerts for critical risks", value=True)
        st.checkbox("SMS alerts for system issues", value=False)
        st.text_input("Alert email", value="admin@example.com")
    
    with settings_tabs[3]:
        st.markdown('<h2 class="professional-subheading">Integration Settings</h2>', unsafe_allow_html=True)
        
        st.markdown('<h3 class="professional-subheading">External Services</h3>', unsafe_allow_html=True)
        st.text_input("Webhook URL", placeholder="https://your-webhook.com/alerts")
        st.selectbox("Export Format", ["JSON", "CSV", "XML"])
        st.checkbox("Enable blockchain explorer links", value=True)
        
        st.markdown('<h3 class="professional-subheading">Database Settings</h3>', unsafe_allow_html=True)
        st.text_input("Backup Location", value="/backups/")
        st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"])

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p>SYNAPSE-LITE Fraud Detection System | Built with Advanced AI Technology</p>
    <p>Real-time Bitcoin transaction monitoring and AI-powered threat detection</p>
</div>
""", unsafe_allow_html=True)