"""
Synapse-Lite Fraud Detection System
Main Streamlit Application

This modular application provides real-time Bitcoin transaction monitoring
and AI-powered fraud detection capabilities.
"""

import streamlit as st
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
    st.markdown("""
    <div class="footer">
        <p>Synapse-Lite Fraud Detection System | Built with Streamlit</p>
        <p>Real-time Bitcoin transaction monitoring and AI-powered threat detection</p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function with routing"""
    # Configure page settings
    configure_page()
    
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
