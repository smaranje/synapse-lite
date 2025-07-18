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
from pages import dashboard, transactions, alerts, analytics, settings
from utils import data_generator, styles, service_integration

# Page configuration
st.set_page_config(
    page_title="Synapse-Lite Fraud Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
styles.apply_custom_css()

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

# Data fetching function
def fetch_data():
    """Fetch data from real services or generate dummy data"""
    if st.session_state.USE_DUMMY_DATA:
        transactions = data_generator.generate_dummy_transactions(100)
        alerts = data_generator.generate_dummy_alerts(transactions)
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
            st.warning("No real data available, using dummy data")
            transactions = data_generator.generate_dummy_transactions(100)
            alerts = data_generator.generate_dummy_alerts(transactions)
    
    return transactions, alerts

# Refresh data if needed
if st.session_state.last_refresh < datetime.now() - timedelta(seconds=REFRESH_INTERVAL):
    st.session_state.transactions, st.session_state.alerts = fetch_data()
    st.session_state.last_refresh = datetime.now()

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🛡️ Synapse-Lite")
    st.markdown("Fraud Detection System")
    st.markdown("---")
    
    # Service status indicators
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
    
    st.markdown("---")
    
    # Navigation menu
    pages_list = ["Dashboard", "Transactions", "Alerts", "Analytics", "Settings"]
    selected_page = st.radio("Navigation", pages_list, label_visibility="collapsed")
    st.session_state.selected_page = selected_page
    
    st.markdown("---")
    
    # Quick stats
    st.markdown("### 📊 Quick Stats")
    total_alerts = len([a for a in st.session_state.alerts if a['status'] == 'Open'])
    critical_alerts = len([a for a in st.session_state.alerts if a['risk_level'] == 'Critical' and a['status'] == 'Open'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Alerts", total_alerts)
    with col2:
        st.metric("Critical", critical_alerts)
    
    avg_risk = np.mean([t['ml_score'] for t in st.session_state.transactions]) * 100 if st.session_state.transactions else 0
    st.metric("Avg Risk Score", f"{avg_risk:.1f}%")
    
    # Data source indicator
    st.markdown("---")
    if st.session_state.USE_DUMMY_DATA:
        st.info("📊 Using Dummy Data")
    else:
        st.success("🔌 Connected to Services")
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.session_state.transactions, st.session_state.alerts = fetch_data()
        st.session_state.last_refresh = datetime.now()
        st.rerun()

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