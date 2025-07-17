"""Settings page for system configuration."""

import streamlit as st

def render_settings():
    """Render the settings page."""
    st.markdown("# Settings")
    st.markdown("### Configure system parameters and preferences")
    
    # Settings tabs
    settings_tabs = st.tabs(["General", "Security", "Monitoring", "Integrations"])
    
    with settings_tabs[0]:
        st.markdown("## General Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Display Preferences")
            st.selectbox("Theme", ["Dark", "Light", "Auto"])
            st.slider("Refresh Rate (seconds)", 1, 60, 5)
            st.checkbox("Show animations", value=True)
            st.checkbox("Enable notifications", value=True)
        
        with col2:
            st.markdown("### Data Settings")
            st.selectbox("Data Source", ["Demo Data", "Live Feed", "Historical"])
            st.slider("Transaction Limit", 10, 1000, 100)
            st.slider("Alert History (days)", 1, 30, 7)
    
    with settings_tabs[1]:
        st.markdown("## Security Settings")
        
        st.markdown("### API Configuration")
        st.text_input("Gemini API Key", type="password", value="••••••••••••••••")
        st.text_input("Neo4j Connection", value="bolt://neo4j:7687")
        
        st.markdown("### Access Control")
        st.checkbox("Enable audit logging", value=True)
        st.checkbox("Require 2FA", value=False)
        st.selectbox("Session timeout", ["15 min", "30 min", "1 hour", "4 hours"])
    
    with settings_tabs[2]:
        st.markdown("## Monitoring Settings")
        
        st.markdown("### Alert Thresholds")
        st.slider("Critical Risk Threshold", 0.0, 1.0, 0.9)
        st.slider("High Risk Threshold", 0.0, 1.0, 0.7)
        st.slider("Medium Risk Threshold", 0.0, 1.0, 0.4)
        
        st.markdown("### Notification Settings")
        st.checkbox("Email alerts for critical risks", value=True)
        st.checkbox("SMS alerts for system issues", value=False)
        st.text_input("Alert email", value="admin@example.com")
    
    with settings_tabs[3]:
        st.markdown("## Integration Settings")
        
        st.markdown("### External Services")
        st.text_input("Webhook URL", placeholder="https://your-webhook.com/alerts")
        st.selectbox("Export Format", ["JSON", "CSV", "XML"])
        st.checkbox("Enable blockchain explorer links", value=True)
        
        st.markdown("### Database Settings")
        st.text_input("Backup Location", value="/backups/")
        st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"])