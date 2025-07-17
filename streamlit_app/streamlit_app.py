"""
Synapse-Lite Fraud Detection System
Main Streamlit Application

This modular application provides real-time Bitcoin transaction monitoring
and AI-powered fraud detection capabilities.
"""

import streamlit as st

def main():
    """Main application entry point."""
    
    # Import configuration and apply page settings
    from config import configure_page
    configure_page()
    
    # Apply styling
    from styling import apply_styling
    apply_styling()
    
    # Render sidebar and get selected page
    from sidebar import render_sidebar
    selected_page = render_sidebar()
    
    # Route to the appropriate page based on selection
    if selected_page == "Dashboard":
        from pages.dashboard import render_dashboard
        render_dashboard()
    elif selected_page == "Transactions":
        from pages.transactions import render_transactions
        render_transactions()
    elif selected_page == "Alerts":
        from pages.alerts import render_alerts
        render_alerts()
    elif selected_page == "Analytics":
        from pages.analytics import render_analytics
        render_analytics()
    elif selected_page == "Settings":
        from pages.settings import render_settings
        render_settings()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>Synapse-Lite Fraud Detection System | Built with Streamlit</p>
        <p>Real-time Bitcoin transaction monitoring and AI-powered threat detection</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
