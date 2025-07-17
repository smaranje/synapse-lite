"""Alerts page for monitoring security alerts."""

import streamlit as st

def render_alerts():
    """Render the security alerts page."""
    st.markdown("# Security Alerts")
    st.markdown("### Monitor and investigate suspicious activity")
    
    # Import here to avoid circular imports
    from ..data_generator import generate_dummy_alerts
    from ..utils import create_metric_card, create_risk_badge
    
    # Alert summary metrics
    alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)
    
    alerts = generate_dummy_alerts(50)
    critical_count = len(alerts[alerts['Risk_Level'] == 'Critical'])
    high_count = len(alerts[alerts['Risk_Level'] == 'High'])
    medium_count = len(alerts[alerts['Risk_Level'] == 'Medium'])
    low_count = len(alerts[alerts['Risk_Level'] == 'Low'])
    
    with alert_col1:
        st.markdown(create_metric_card("Critical", str(critical_count), "Immediate action", "negative"), unsafe_allow_html=True)
    with alert_col2:
        st.markdown(create_metric_card("High", str(high_count), "Review required", "neutral"), unsafe_allow_html=True)
    with alert_col3:
        st.markdown(create_metric_card("Medium", str(medium_count), "Monitor closely", "neutral"), unsafe_allow_html=True)
    with alert_col4:
        st.markdown(create_metric_card("Low", str(low_count), "Standard review", "positive"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Alert filters
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
    
    with filter_col1:
        alert_search = st.text_input("Search alerts", placeholder="Enter transaction hash or details")
    with filter_col2:
        severity_filter = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])
    with filter_col3:
        if st.button("Refresh Alerts", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Alert list
    if not alerts.empty:
        # Apply filters
        if severity_filter != "All":
            alerts = alerts[alerts['Risk_Level'] == severity_filter]
        if alert_search:
            alerts = alerts[alerts['Hash'].str.contains(alert_search, case=False, na=False)]
        
        # Sort by risk level and timestamp
        alerts = alerts.sort_values(['Risk_Level', 'Timestamp'], ascending=[True, False])
        
        for _, alert in alerts.iterrows():
            risk_level = alert['Risk_Level']
            description = "Unusual transaction pattern detected"
            
            if alert['Smurfing_Rule']:
                description = "Smurfing pattern detected: Multiple small outputs"
            elif alert['ML_Score'] >= 0.9:
                description = "High ML fraud score detected"
            elif alert['ML_Score'] >= 0.7:
                description = "Elevated fraud risk identified"
            
            st.markdown(f"""
            <div class="alert-card {risk_level.lower()}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">
                            {create_risk_badge(risk_level)} Alert #{alert['Hash'][:8]}...
                        </div>
                        <div style="color: #e2e8f0; margin-bottom: 0.75rem;">{description}</div>
                        <div style="color: #a0aec0; font-size: 0.9rem;">
                            <strong>Transaction:</strong> {alert['Hash'][:16]}...<br>
                            <strong>Amount:</strong> {alert['TotalOutputValue']/1e8:.4f} BTC<br>
                            <strong>Time:</strong> {alert['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No alerts found matching your criteria.")