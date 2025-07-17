"""Configuration file for Streamlit app."""

import streamlit as st

# Configuration constants
USE_DUMMY_DATA = True
BTC_USD_RATE = 65000

# App configuration
APP_TITLE = "Synapse-Lite Fraud Detector"
APP_ICON = "🔷"

# Page configuration
PAGE_CONFIG = {
    "layout": "wide", 
    "page_title": APP_TITLE,
    "page_icon": APP_ICON,
    "initial_sidebar_state": "expanded"
}

# Navigation pages with icons
PAGES = {
    "Dashboard": "🏠",
    "Transactions": "💰", 
    "Alerts": "🚨",
    "Analytics": "📊",
    "Settings": "⚙️"
}

def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(**PAGE_CONFIG)
