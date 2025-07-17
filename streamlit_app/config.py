import streamlit as st

# Configuration
USE_DUMMY_DATA = True
BTC_USD_RATE = 65000

# Page configuration
PAGE_CONFIG = {
    "layout": "wide", 
    "page_title": "Synapse-Lite Fraud Detector",
    "page_icon": "🔷",
    "initial_sidebar_state": "expanded"
}

# Navigation pages
PAGES = {
    "Dashboard": "Dashboard",
    "Transactions": "Transactions", 
    "Alerts": "Alerts",
    "Analytics": "Analytics",
    "Settings": "Settings"
}

def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(**PAGE_CONFIG)