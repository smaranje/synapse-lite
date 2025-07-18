"""
Synapse-Lite Fraud Detection Dashboard
Main Application File
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import time
import random
from typing import Dict, List, Tuple, Optional
import hashlib
import os

# Import page modules
from modules import dashboard, transactions, alerts, analytics, settings
from utils import data_generator, styles, service_integration, theme_manager

# Page configuration
st.set_page_config(
    page_title="Synapse-Lite Fraud Detector",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme
theme_manager.init_theme()

# Apply custom CSS
styles.apply_custom_css()

# Simple loading message CSS
st.markdown("""
<style>
.loading-message {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    color: #333;
    padding: 12px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    border-left: 4px solid #2196F3;
    z-index: 1000;
    font-size: 14px;
}

.success-message {
    border-left-color: #4CAF50;
}

.loading-dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #2196F3;
    margin-right: 8px;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# Apply theme override if set
st.markdown(theme_manager.get_theme_override_css(), unsafe_allow_html=True)

# Configuration
if 'USE_DUMMY_DATA' not in st.session_state:
    st.session_state.USE_DUMMY_DATA = os.getenv("USE_DUMMY_DATA", "true").lower() == "true"

FLASK_LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://flask-llm-service:5000")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "5"))

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "Dashboard"
if 'service_status' not in st.session_state:
    st.session_state.service_status = {
        'neo4j': False,
        'kafka': False,
        'llm': False
    }

# Initialize service connections
if not st.session_state.USE_DUMMY_DATA:
    neo4j_conn = service_integration.get_neo4j_connection()
    kafka_conn = service_integration.get_kafka_connection()
    llm_conn = service_integration.get_llm_connection()
    
    # Check service status
    st.session_state.service_status['neo4j'] = neo4j_conn.driver is not None
    st.session_state.service_status['kafka'] = kafka_conn.create_consumer()
    st.session_state.service_status['llm'] = llm_conn.check_health()

# Simple message function
def show_simple_message(message, is_success=False):
    """Show a simple loading or success message"""
    message_class = "loading-message success-message" if is_success else "loading-message"
    icon = "✅" if is_success else '<div class="loading-dot"></div>'
    
    return st.markdown(f"""
    <div class="{message_class}" id="status-message">
        {icon} {message}
    </div>
    <script>
        setTimeout(function() {{
            var msg = document.getElementById('status-message');
            if (msg) msg.remove();
        }}, 3000);
    </script>
    """, unsafe_allow_html=True)

# Data fetching function with simple messages
def fetch_data():
    """Fetch data from real services or generate dummy data"""
    
    # Show loading message
    message_placeholder = st.empty()
    with message_placeholder:
        show_simple_message("Refreshing data...")
    
    if st.session_state.USE_DUMMY_DATA:
        # Small delay to show loading message
        time.sleep(0.8)
        transactions = data_generator.generate_dummy_transactions(100)
        alerts = data_generator.generate_dummy_alerts(transactions)
        
        # Show success message
        with message_placeholder:
            show_simple_message(f"Loaded {len(transactions)} transactions", True)
    else:
        # Fetch from Neo4j
        neo4j_conn = service_integration.get_neo4j_connection()
        transactions = neo4j_conn.get_recent_transactions(100)
        alerts = neo4j_conn.get_alerts()
        
        # If no data from Neo4j, check Kafka for real-time updates
        if not transactions:
            kafka_conn = service_integration.get_kafka_connection()
            if kafka_conn.create_consumer():
                kafka_messages = kafka_conn.consume_messages(10)
                # Convert Kafka messages to transaction format
                for msg in kafka_messages:
                    if 'hash' in msg:
                        transactions.append(msg)
        
        # If still no data, fall back to dummy data
        if not transactions:
            with message_placeholder:
                show_simple_message("Using demo data", True)
            transactions = data_generator.generate_dummy_transactions(100)
            alerts = data_generator.generate_dummy_alerts(transactions)
        else:
            with message_placeholder:
                show_simple_message(f"Loaded {len(transactions)} live transactions", True)
    
    # Clear message after a moment
    time.sleep(1)
    message_placeholder.empty()
    
    return transactions, alerts

# Refresh data if needed
if st.session_state.last_refresh < datetime.now() - timedelta(seconds=REFRESH_INTERVAL):
    st.session_state.transactions, st.session_state.alerts = fetch_data()
    st.session_state.last_refresh = datetime.now()

# Professional header with clean title
st.markdown("""
<div style="text-align: center; padding: 20px 0 30px 0; border-bottom: 1px solid #e5e7eb;">
    <h1 style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               font-weight: 600; 
               font-size: 32px; 
               color: #1f2937; 
               margin: 0; 
               letter-spacing: -0.025em;">
        Synapse-Lite
    </h1>
    <p style="font-family: 'Inter', sans-serif; 
              font-size: 16px; 
              color: #6b7280; 
              margin: 8px 0 0 0; 
              font-weight: 400;">
        Fraud Detection System
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    # Logo
    st.image("coinbase.svg", width=80)
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
    
    # Navigation menu (moved up)
    pages_list = ["Dashboard", "Transactions", "Alerts", "Analytics", "Settings"]
    selected_page = st.radio("Navigation", pages_list, label_visibility="collapsed")
    st.session_state.selected_page = selected_page
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("### Quick Stats")
    total_alerts = len([a for a in st.session_state.alerts if a['status'] == 'Open'])
    critical_alerts = len([a for a in st.session_state.alerts if a['risk_level'] == 'Critical' and a['status'] == 'Open'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Alerts", total_alerts)
    with col2:
        st.metric("Critical", critical_alerts)
    
    avg_risk = np.mean([t['ml_score'] for t in st.session_state.transactions]) * 100 if st.session_state.transactions else 0
    st.metric("Avg Risk Score", f"{avg_risk:.1f}%")
    
    # Service status indicators
    st.markdown("---")
    st.markdown("#### Service Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.service_status.get('neo4j', False):
            st.success("Neo4j ✓")
        else:
            st.error("Neo4j ✗")
    
    with col2:
        if st.session_state.service_status.get('kafka', False):
            st.success("Kafka ✓")
        else:
            st.error("Kafka ✗")
    
    with col3:
        if st.session_state.service_status.get('llm', False):
            st.success("LLM ✓")
        else:
            st.error("LLM ✗")
    
    # Refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.session_state.transactions, st.session_state.alerts = fetch_data()
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    # Theme toggle
    theme_manager.render_theme_toggle()

# Main content area based on selected page
if st.session_state.selected_page == "Dashboard":
    dashboard.show()
elif st.session_state.selected_page == "Transactions":
    transactions.show()
elif st.session_state.selected_page == "Alerts":
    alerts.show()
elif st.session_state.selected_page == "Analytics":
    analytics.show()
elif st.session_state.selected_page == "Settings":
    settings.show()

# Footer
st.markdown("""
<div style="text-align: center; padding: 20px 0; margin-top: 50px; border-top: 1px solid #e5e7eb;">
    <span style="font-family: 'Inter', sans-serif; font-size: 12px; color: #6b7280; font-weight: 500;">
        SMARAN TECH
    </span>
    <br>
    <span style="font-family: 'Inter', sans-serif; font-size: 11px; color: #9ca3af; margin-top: 4px; display: inline-block;">
        Made by Smaranjeet Singh
    </span>
</div>
""", unsafe_allow_html=True)