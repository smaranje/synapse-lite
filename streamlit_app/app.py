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

# Import page modules
from pages import dashboard, transactions, alerts, analytics, settings
from utils import data_generator, styles

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
    st.session_state.USE_DUMMY_DATA = True

FLASK_LLM_SERVICE_URL = "http://flask-llm-service:5000"
REFRESH_INTERVAL = 5  # seconds

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'alerts' not in st.session_state:
    st.session_state.alerts = []
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "Dashboard"

# Refresh data if needed
if st.session_state.last_refresh < datetime.now() - timedelta(seconds=REFRESH_INTERVAL):
    st.session_state.transactions = data_generator.generate_dummy_transactions(100)
    st.session_state.alerts = data_generator.generate_dummy_alerts(st.session_state.transactions)
    st.session_state.last_refresh = datetime.now()

# Sidebar navigation
with st.sidebar:
    st.markdown("### 🛡️ Synapse-Lite")
    st.markdown("Fraud Detection System")
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
    
    # Refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.session_state.transactions = data_generator.generate_dummy_transactions(100)
        st.session_state.alerts = data_generator.generate_dummy_alerts(st.session_state.transactions)
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