"""
Synapse-Lite Fraud Detection Dashboard with Loading Messages
Enhanced Application File with User-Friendly Data Loading Notifications
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
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme
theme_manager.init_theme()

# Apply custom CSS with loading popup styles
def apply_loading_css():
    """Apply custom CSS including loading popup styles"""
    styles.apply_custom_css()
    
    # Enhanced CSS for loading popups and notifications
    st.markdown("""
    <style>
    /* Loading Popup Styles */
    .loading-popup {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        z-index: 9999;
        text-align: center;
        font-family: 'Inter', sans-serif;
        min-width: 300px;
        animation: slideIn 0.3s ease-out;
    }
    
    .loading-popup-success {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .loading-popup-warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    @keyframes slideIn {
        from { transform: translate(-50%, -60%); opacity: 0; }
        to { transform: translate(-50%, -50%); opacity: 1; }
    }
    
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
        margin-right: 10px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Data refresh notification */
    .data-refresh-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(34, 197, 94, 0.9);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 500;
        z-index: 1000;
        animation: slideInRight 0.3s ease-out;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* Service status enhanced */
    .service-status {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 5px 0;
    }
    
    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    
    .status-connected {
        background-color: #10b981;
        animation: pulse 2s infinite;
    }
    
    .status-disconnected {
        background-color: #ef4444;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Loading cards */
    .loading-card {
        background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        height: 100px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    </style>
    """, unsafe_allow_html=True)

apply_loading_css()

# Apply theme override if set
st.markdown(theme_manager.get_theme_override_css(), unsafe_allow_html=True)

# Configuration
if 'USE_DUMMY_DATA' not in st.session_state:
    st.session_state.USE_DUMMY_DATA = os.getenv("USE_DUMMY_DATA", "true").lower() == "true"

FLASK_LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://flask-llm-service:5000")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "10"))
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")

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
if 'loading_state' not in st.session_state:
    st.session_state.loading_state = {
        'is_loading': False,
        'message': '',
        'type': 'info'  # info, success, warning, error
    }
if 'data_stats' not in st.session_state:
    st.session_state.data_stats = {
        'total_transactions': 0,
        'last_transaction_time': None,
        'data_flow_rate': 0
    }

def show_loading_popup(message: str, popup_type: str = "info", duration: float = 2.0):
    """Show a loading popup message"""
    popup_class = f"loading-popup loading-popup-{popup_type}"
    
    if popup_type == "info":
        icon = "🔄"
        spinner = '<div class="loading-spinner"></div>'
    elif popup_type == "success":
        icon = "✅"
        spinner = ""
    elif popup_type == "warning":
        icon = "⚠️"
        spinner = ""
    else:
        icon = "❌"
        spinner = ""
    
    popup_html = f"""
    <div class="{popup_class}" id="loading-popup">
        {spinner}{icon} {message}
    </div>
    <script>
        setTimeout(function() {{
            var popup = document.getElementById('loading-popup');
            if (popup) {{
                popup.style.opacity = '0';
                setTimeout(function() {{
                    popup.remove();
                }}, 300);
            }}
        }}, {duration * 1000});
    </script>
    """
    
    return st.markdown(popup_html, unsafe_allow_html=True)

def show_data_refresh_notification(new_data_count: int):
    """Show data refresh notification"""
    notification_html = f"""
    <div class="data-refresh-notification" id="refresh-notification">
        🔄 Data refreshed! {new_data_count} new transactions loaded
    </div>
    <script>
        setTimeout(function() {{
            var notification = document.getElementById('refresh-notification');
            if (notification) {{
                notification.style.opacity = '0';
                setTimeout(function() {{
                    notification.remove();
                }}, 300);
            }}
        }}, 3000);
    </script>
    """
    return st.markdown(notification_html, unsafe_allow_html=True)

def check_service_health():
    """Check the health of all services with loading messages"""
    st.session_state.loading_state = {'is_loading': True, 'message': 'Checking service health...', 'type': 'info'}
    
    health_status = {'neo4j': False, 'kafka': False, 'llm': False}
    
    # Check Neo4j
    try:
        if not st.session_state.USE_DUMMY_DATA:
            neo4j_conn = service_integration.get_neo4j_connection()
            health_status['neo4j'] = neo4j_conn.driver is not None
        else:
            health_status['neo4j'] = True  # Dummy mode
    except Exception as e:
        st.warning(f"Neo4j health check failed: {str(e)}")
    
    # Check Kafka
    try:
        if not st.session_state.USE_DUMMY_DATA:
            kafka_conn = service_integration.get_kafka_connection()
            health_status['kafka'] = kafka_conn.create_consumer()
        else:
            health_status['kafka'] = True  # Dummy mode
    except Exception as e:
        st.warning(f"Kafka health check failed: {str(e)}")
    
    # Check LLM Service
    try:
        if not st.session_state.USE_DUMMY_DATA:
            llm_conn = service_integration.get_llm_connection()
            health_status['llm'] = llm_conn.check_health()
        else:
            health_status['llm'] = True  # Dummy mode
    except Exception as e:
        st.warning(f"LLM service health check failed: {str(e)}")
    
    st.session_state.service_status = health_status
    st.session_state.loading_state = {'is_loading': False, 'message': '', 'type': 'info'}
    
    return health_status

# Data fetching function with loading messages
def fetch_data():
    """Fetch data from real services or generate dummy data with loading messages"""
    
    # Show loading popup
    loading_placeholder = st.empty()
    with loading_placeholder:
        show_loading_popup("Loading fresh transaction data...", "info", 2.0)
    
    start_time = time.time()
    new_transactions = []
    new_alerts = []
    
    if st.session_state.USE_DUMMY_DATA:
        # Simulate data loading delay
        time.sleep(1)
        new_transactions = data_generator.generate_dummy_transactions(100)
        new_alerts = data_generator.generate_dummy_alerts(new_transactions)
        
        # Show success message
        with loading_placeholder:
            show_loading_popup("Demo data loaded successfully!", "success", 2.0)
    else:
        try:
            # Step 1: Try Neo4j
            with loading_placeholder:
                show_loading_popup("Connecting to Neo4j database...", "info", 1.5)
            
            neo4j_conn = service_integration.get_neo4j_connection()
            if neo4j_conn.driver:
                new_transactions = neo4j_conn.get_recent_transactions(100)
                new_alerts = neo4j_conn.get_alerts()
                
                if new_transactions:
                    with loading_placeholder:
                        show_loading_popup(f"Found {len(new_transactions)} transactions in Neo4j!", "success", 2.0)
            
            # Step 2: If no Neo4j data, try Kafka
            if not new_transactions:
                with loading_placeholder:
                    show_loading_popup("Checking Kafka for real-time data...", "info", 1.5)
                
                kafka_conn = service_integration.get_kafka_connection()
                if kafka_conn.create_consumer():
                    kafka_messages = kafka_conn.consume_messages(10)
                    for msg in kafka_messages:
                        if 'hash' in msg:
                            new_transactions.append(msg)
                    
                    if new_transactions:
                        with loading_placeholder:
                            show_loading_popup(f"Loaded {len(new_transactions)} real-time transactions!", "success", 2.0)
            
            # Step 3: Fallback to dummy data
            if not new_transactions:
                with loading_placeholder:
                    show_loading_popup("No live data found, generating demo data...", "warning", 2.0)
                
                new_transactions = data_generator.generate_dummy_transactions(100)
                new_alerts = data_generator.generate_dummy_alerts(new_transactions)
                
        except Exception as e:
            with loading_placeholder:
                show_loading_popup(f"Error loading data: {str(e)[:50]}...", "error", 3.0)
            
            # Fallback to dummy data
            new_transactions = data_generator.generate_dummy_transactions(100)
            new_alerts = data_generator.generate_dummy_alerts(new_transactions)
    
    # Update statistics
    load_time = time.time() - start_time
    st.session_state.data_stats['total_transactions'] = len(new_transactions)
    st.session_state.data_stats['last_transaction_time'] = datetime.now()
    st.session_state.data_stats['data_flow_rate'] = len(new_transactions) / max(load_time, 0.1)
    
    # Clear loading popup
    time.sleep(0.5)
    loading_placeholder.empty()
    
    return new_transactions, new_alerts

# Auto-refresh data with notifications
def auto_refresh_data():
    """Auto-refresh data and show notifications"""
    if st.session_state.last_refresh < datetime.now() - timedelta(seconds=REFRESH_INTERVAL):
        old_count = len(st.session_state.transactions)
        
        # Fetch new data
        st.session_state.transactions, st.session_state.alerts = fetch_data()
        st.session_state.last_refresh = datetime.now()
        
        new_count = len(st.session_state.transactions)
        
        # Show refresh notification if there's new data
        if new_count > old_count:
            show_data_refresh_notification(new_count - old_count)

# Check service health on startup
if 'health_checked' not in st.session_state:
    check_service_health()
    st.session_state.health_checked = True

# Auto-refresh data
auto_refresh_data()

# Top header with branding and status
st.markdown("""
<div style="position: fixed; top: 0; right: 20px; z-index: 999; padding: 10px 0;">
    <span style="font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-weight: 500; font-size: 13px; color: #6b7280; letter-spacing: 0.5px;">SYNAPSE TECH</span>
</div>
""", unsafe_allow_html=True)

# Real-time data status indicator
data_status_color = "#10b981" if st.session_state.data_stats['last_transaction_time'] else "#ef4444"
last_update = st.session_state.data_stats['last_transaction_time']
last_update_str = last_update.strftime("%H:%M:%S") if last_update else "Never"

st.markdown(f"""
<div style="position: fixed; top: 0; left: 20px; z-index: 999; padding: 10px 0;">
    <div style="display: flex; align-items: center; gap: 8px;">
        <div class="status-indicator" style="background-color: {data_status_color};"></div>
        <span style="font-family: 'Inter', sans-serif; font-size: 12px; color: #6b7280;">
            Last Update: {last_update_str} | {st.session_state.data_stats['total_transactions']} transactions
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar navigation with enhanced service status
with st.sidebar:
    # Logo
    st.image("coinbase.svg", width=80)
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    st.markdown("### **Synapse-Lite**")
    st.markdown("Fraud Detection System")
    st.markdown("---")
    
    # Navigation menu
    pages_list = ["Dashboard", "Transactions", "Alerts", "Analytics", "Settings"]
    selected_page = st.radio("Navigation", pages_list, label_visibility="collapsed")
    st.session_state.selected_page = selected_page
    
    st.markdown("---")
    
    # Data flow statistics
    st.markdown("### Data Flow Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total TX", st.session_state.data_stats['total_transactions'])
    with col2:
        st.metric("Rate/sec", f"{st.session_state.data_stats['data_flow_rate']:.1f}")
    
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
    
    # Enhanced service status indicators
    st.markdown("---")
    st.markdown("#### Service Status")
    
    services = [
        ("Neo4j", st.session_state.service_status.get('neo4j', False)),
        ("Kafka", st.session_state.service_status.get('kafka', False)),
        ("LLM AI", st.session_state.service_status.get('llm', False))
    ]
    
    for service_name, is_connected in services:
        status_class = "status-connected" if is_connected else "status-disconnected"
        status_text = "Connected" if is_connected else "Disconnected"
        status_icon = "✅" if is_connected else "❌"
        
        st.markdown(f"""
        <div class="service-status">
            <div class="status-indicator {status_class}"></div>
            <span style="font-size: 14px; font-weight: 500;">{service_name}</span>
            <span style="font-size: 12px; color: #6b7280;">{status_icon}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced refresh button with loading state
    st.markdown("---")
    refresh_col1, refresh_col2 = st.columns([3, 1])
    
    with refresh_col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            show_loading_popup("Refreshing all data sources...", "info", 1.0)
            old_count = len(st.session_state.transactions)
            st.session_state.transactions, st.session_state.alerts = fetch_data()
            st.session_state.last_refresh = datetime.now()
            new_count = len(st.session_state.transactions)
            
            if new_count != old_count:
                show_data_refresh_notification(abs(new_count - old_count))
            
            st.rerun()
    
    with refresh_col2:
        if st.button("🔧", help="Check service health"):
            show_loading_popup("Checking all services...", "info", 1.0)
            check_service_health()
            st.rerun()
    
    # Auto-refresh settings
    st.markdown("---")
    st.markdown("#### Auto-Refresh")
    auto_refresh = st.checkbox("Enable auto-refresh", value=True)
    if auto_refresh:
        refresh_seconds = st.slider("Interval (seconds)", 5, 60, REFRESH_INTERVAL)
        next_refresh = st.session_state.last_refresh + timedelta(seconds=refresh_seconds)
        seconds_remaining = max(0, (next_refresh - datetime.now()).total_seconds())
        st.write(f"Next refresh in: {int(seconds_remaining)}s")
    
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

# Footer with data freshness indicator
current_time = datetime.now()
time_since_refresh = (current_time - st.session_state.last_refresh).total_seconds()
freshness_color = "#10b981" if time_since_refresh < 30 else "#f59e0b" if time_since_refresh < 60 else "#ef4444"

st.markdown(f"""
<div style="text-align: center; padding: 20px 0; margin-top: 50px; border-top: 1px solid #e5e7eb;">
    <div style="margin-bottom: 10px;">
        <span style="font-size: 12px; color: {freshness_color};">
            ● Data freshness: {int(time_since_refresh)}s ago
        </span>
    </div>
    <span style="font-family: 'Inter', sans-serif; font-size: 12px; color: #6b7280;">
        Made by Smaranjeet Singh | Real-time Fraud Detection
    </span>
</div>
""", unsafe_allow_html=True)

# Auto-rerun for real-time updates (if auto-refresh is enabled)
if 'auto_refresh' in locals() and auto_refresh:
    time.sleep(1)
    st.rerun()