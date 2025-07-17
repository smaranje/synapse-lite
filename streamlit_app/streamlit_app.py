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
import sys
import os

# Add the current directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import USE_DUMMY_DATA, BTC_USD_RATE, APP_TITLE, APP_ICON

def apply_styling():
    """Apply the Coinbase-inspired CSS styling"""
    st.set_page_config(
        layout="wide", 
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        initial_sidebar_state="expanded"
    )

    # Coinbase-inspired CSS with professional fintech design
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        .main {
            background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
            color: #1a1a1a;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        }
        
        /* Header styling */
        h1 {
            color: #0a0b0d;
            font-weight: 600;
            font-size: 2.25rem;
            text-align: center;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }
        
        h2, h3 {
            color: #1a1a1a;
            font-weight: 500;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            letter-spacing: -0.01em;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
            border-right: 1px solid #f0f3f7;
        }
        
        /* Main content area */
        .css-1v0mbdj {
            padding: 2rem 1rem;
        }
        
        /* Metric styling */
        .css-1xarl3l {
            background: white;
            border: 1px solid #f0f3f7;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        
        /* Button styling */
        .stButton > button {
            background: #0052ff;
            color: white;
            border: none;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 0.875rem;
            padding: 0.625rem 1rem;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background: #0046cc;
            transform: translateY(-1px);
        }
        
        /* Chart styling */
        .js-plotly-plot .plotly .modebar {
            right: 10px;
        }
        
        /* Custom card styling */
        .metric-card {
            background: white;
            border: 1px solid #f0f3f7;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            font-family: 'Inter', sans-serif;
            font-size: 0.875rem;
            font-weight: 500;
            color: #1a1a1a;
            transition: all 0.2s ease;
        }
        
        .metric-card:hover {
            border-color: #0052ff;
            background: #f8faff;
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            padding: 2rem 0;
            color: #6b7280;
            font-size: 0.875rem;
            border-top: 1px solid #f0f3f7;
            margin-top: 3rem;
        }
        </style>
        """, unsafe_allow_html=True)

def main():
    """Main application function"""
    # Apply styling
    apply_styling()
    
    # Render sidebar and get selected page
    from sidebar import render_sidebar
    selected_page = render_sidebar()
    
    # Route to the appropriate page based on selection
    if selected_page == "Dashboard":
        render_dashboard()
    elif selected_page == "Transactions":
        render_transactions()
    elif selected_page == "Alerts":
        render_alerts()
    elif selected_page == "Analytics":
        render_analytics()
    elif selected_page == "Settings":
        render_settings()

def render_dashboard():
    """Render the main dashboard page"""
    st.title("🏠 Dashboard")
    st.markdown("### Real-time Fraud Detection Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Transactions Today", "12,847", "+5.2%")
    with col2:
        st.metric("Fraud Alerts", "23", "+12%")
    with col3:
        st.metric("Risk Score", "68%", "-3%")
    with col4:
        st.metric("System Uptime", "99.9%", "0%")
    
    # Charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Transaction Volume (24h)")
        # Generate dummy data
        hours = list(range(24))
        volumes = [random.randint(200, 800) for _ in hours]
        
        fig = px.line(x=hours, y=volumes, title="Hourly Transaction Volume")
        fig.update_layout(
            xaxis_title="Hour",
            yaxis_title="Transactions",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Risk Distribution")
        risk_levels = ["Low", "Medium", "High", "Critical"]
        risk_counts = [45, 30, 20, 5]
        
        fig = px.pie(values=risk_counts, names=risk_levels, title="Risk Level Distribution")
        st.plotly_chart(fig, use_container_width=True)

def render_transactions():
    """Render the transactions page"""
    st.title("💰 Transactions")
    st.markdown("### Recent Bitcoin Transactions")
    
    # Generate dummy transaction data
    transactions = []
    for i in range(50):
        tx = {
            "ID": hashlib.md5(f"tx_{i}_{random.randint(1000, 9999)}".encode()).hexdigest()[:8],
            "Amount (BTC)": round(random.uniform(0.001, 10.0), 6),
            "USD Value": 0,  # Will calculate
            "Risk Score": random.randint(1, 100),
            "Status": random.choice(["Confirmed", "Pending", "Flagged"]),
            "Timestamp": datetime.now() - timedelta(minutes=random.randint(1, 1440))
        }
        tx["USD Value"] = round(tx["Amount (BTC)"] * BTC_USD_RATE, 2)
        transactions.append(tx)
    
    df = pd.DataFrame(transactions)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Confirmed", "Pending", "Flagged"])
    with col2:
        min_risk = st.slider("Minimum Risk Score", 0, 100, 0)
    with col3:
        max_amount = st.number_input("Max Amount (BTC)", value=10.0)
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]
    filtered_df = filtered_df[filtered_df["Risk Score"] >= min_risk]
    filtered_df = filtered_df[filtered_df["Amount (BTC)"] <= max_amount]
    
    st.dataframe(filtered_df, use_container_width=True)

def render_alerts():
    """Render the alerts page"""
    st.title("🚨 Fraud Alerts")
    st.markdown("### Active Security Alerts")
    
    # Generate dummy alerts
    alerts = []
    alert_types = ["Suspicious Pattern", "High-Risk Transaction", "Account Anomaly", "Multiple Failures"]
    
    for i in range(15):
        alert = {
            "ID": f"ALERT-{random.randint(1000, 9999)}",
            "Type": random.choice(alert_types),
            "Severity": random.choice(["Low", "Medium", "High", "Critical"]),
            "Description": f"Detected suspicious activity in transaction pattern #{random.randint(100, 999)}",
            "Timestamp": datetime.now() - timedelta(minutes=random.randint(1, 720)),
            "Status": random.choice(["Open", "Investigating", "Resolved"])
        }
        alerts.append(alert)
    
    alert_df = pd.DataFrame(alerts)
    
    # Alert summary
    col1, col2, col3 = st.columns(3)
    with col1:
        open_alerts = len(alert_df[alert_df["Status"] == "Open"])
        st.metric("Open Alerts", open_alerts)
    with col2:
        critical_alerts = len(alert_df[alert_df["Severity"] == "Critical"])
        st.metric("Critical Alerts", critical_alerts)
    with col3:
        resolved_today = len(alert_df[alert_df["Status"] == "Resolved"])
        st.metric("Resolved Today", resolved_today)
    
    # Alerts table
    st.dataframe(alert_df, use_container_width=True)

def render_analytics():
    """Render the analytics page"""
    st.title("📊 Analytics")
    st.markdown("### Fraud Detection Analytics")
    
    # Generate analytics data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Monthly Fraud Detection Rate")
        monthly_data = {
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Detection Rate': [92.5, 94.1, 91.8, 95.2, 93.7, 96.1]
        }
        fig = px.bar(monthly_data, x='Month', y='Detection Rate', title="Fraud Detection Accuracy")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Transaction Risk Trends")
        trend_data = {
            'Week': list(range(1, 13)),
            'High Risk': [random.randint(10, 50) for _ in range(12)],
            'Medium Risk': [random.randint(50, 100) for _ in range(12)],
            'Low Risk': [random.randint(200, 400) for _ in range(12)]
        }
        fig = px.line(trend_data, x='Week', y=['High Risk', 'Medium Risk', 'Low Risk'],
                     title="Weekly Risk Trends")
        st.plotly_chart(fig, use_container_width=True)

def render_settings():
    """Render the settings page"""
    st.title("⚙️ Settings")
    st.markdown("### System Configuration")
    
    # Detection settings
    st.subheader("Detection Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        st.slider("Risk Threshold", 0, 100, 70)
        st.selectbox("Alert Frequency", ["Real-time", "Every 5 min", "Hourly"])
        st.checkbox("Auto-block high-risk transactions", value=True)
    
    with col2:
        st.number_input("Max Transaction Amount ($)", value=10000)
        st.selectbox("Notification Method", ["Email", "SMS", "Both"])
        st.checkbox("Enable ML model updates", value=True)
    
    # System settings
    st.subheader("System Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Neo4j Connection", value="bolt://neo4j:7687")
        st.text_input("Admin Email", value="admin@company.com")
        st.selectbox("Log Level", ["INFO", "DEBUG", "WARNING", "ERROR"])
        st.selectbox("Session timeout", ["15 min", "30 min", "1 hour", "4 hours"])
    
    with col2:
        st.text_input("API Endpoint", value="http://ai-service:5000")
        st.number_input("API Timeout (seconds)", value=30)
        st.checkbox("Enable detailed logging", value=False)
        st.checkbox("Enable performance monitoring", value=True)

# Footer
def render_footer():
    """Render the application footer"""
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>Synapse-Lite Fraud Detection System | Built with Streamlit</p>
        <p>Real-time Bitcoin transaction monitoring and AI-powered threat detection</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    render_footer()