"""
Synapse-Lite Fraud Detection System
Main Streamlit Application

This modular application provides real-time Bitcoin transaction monitoring
and AI-powered fraud detection capabilities.
"""

import streamlit as st
from config import APP_TITLE, APP_ICON

st.set_page_config(
    layout="wide",
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    initial_sidebar_state="expanded"
)

# Custom header for branding
st.markdown(
    """
    <div style="position: fixed; top: 0; right: 0; width: 100%; z-index: 9999; background: white; border-bottom: 1px solid #f0f3f7; display: flex; justify-content: flex-end; align-items: center; height: 48px;">
        <span style="font-size: 1.1rem; font-weight: 700; color: #0052ff; margin-right: 2rem; letter-spacing: 2px;">SMARAN TECHNOLOGIES</span>
    </div>
    <div style="height: 48px;"></div>
    """,
    unsafe_allow_html=True
)

import sys
import os

# Add the current directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core modules
from config import configure_page
from styling import apply_styling
from sidebar import render_sidebar

# Import page modules
from pages.dashboard import render_dashboard
from pages.transactions import render_transactions
from pages.alerts import render_alerts
from pages.analytics import render_analytics
from pages.settings import render_settings

def render_footer():
    """Render the application footer"""
    st.markdown("---")
    st.markdown(
        """
        <div class="footer">
            <p>Synapse-Lite Fraud Detection System | Built with Streamlit</p>
            <p>Real-time Bitcoin transaction monitoring and AI-powered threat detection</p>
            <p style='font-size:0.9rem; color:#6b7280;'>Made by Smaranjeet Singh</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def main():
    """Main application function with routing"""
    # Configure page settings
    # configure_page()  # No longer needed, handled by st.set_page_config
    
    # Apply styling
    apply_styling()
    
    # Render sidebar and get selected page
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
    else:
        # Default to dashboard if unknown page
        render_dashboard()
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()
