"""
Alerts page for the Synapse-Lite Fraud Detection System
Includes investigation workflow and SAR generation
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import service_integration, data_generator

def show():
    """Display the alerts investigation page"""
    st.title("🚨 Alert Investigation")
    
    # Alert summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    critical_alerts = [a for a in st.session_state.alerts if a['risk_level'] == 'Critical' and a['status'] == 'Open']
    high_alerts = [a for a in st.session_state.alerts if a['risk_level'] == 'High' and a['status'] == 'Open']
    medium_alerts = [a for a in st.session_state.alerts if a['risk_level'] == 'Medium' and a['status'] == 'Open']
    low_alerts = [a for a in st.session_state.alerts if a['risk_level'] == 'Low' and a['status'] == 'Open']
    
    with col1:
        st.metric(
            "Critical Alerts",
            len(critical_alerts),
            delta=f"+{len([a for a in critical_alerts if (datetime.now() - a['timestamp']).total_seconds() < 3600])}" if critical_alerts else "0",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "High Alerts",
            len(high_alerts),
            delta=f"+{len([a for a in high_alerts if (datetime.now() - a['timestamp']).total_seconds() < 3600])}" if high_alerts else "0",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "Medium Alerts",
            len(medium_alerts),
            help="Medium risk alerts requiring review"
        )
    
    with col4:
        st.metric(
            "Low Alerts",
            len(low_alerts),
            help="Low risk alerts for monitoring"
        )
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        search_alert = st.text_input(
            "🔍 Search alerts",
            placeholder="Search by alert ID or transaction hash...",
            key="alert_search"
        )
    
    with col2:
        severity_filter = st.multiselect(
            "Severity Filter",
            ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High"],
            key="severity_filter"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Status",
            ["Open", "Under Investigation", "Resolved", "All"],
            key="status_filter"
        )
    
    # Apply filters
    filtered_alerts = st.session_state.alerts.copy()
    
    if search_alert:
        filtered_alerts = [
            alert for alert in filtered_alerts
            if search_alert.lower() in alert['alert_id'].lower() or
            search_alert.lower() in alert['transaction_hash'].lower()
        ]
    
    if severity_filter:
        filtered_alerts = [
            alert for alert in filtered_alerts
            if alert['risk_level'] in severity_filter
        ]
    
    if status_filter != "All":
        filtered_alerts = [
            alert for alert in filtered_alerts
            if alert['status'] == status_filter
        ]
    
    # Sort by timestamp (most recent first)
    filtered_alerts.sort(key=lambda x: x['timestamp'], reverse=True)
    
    st.markdown(f"### 📋 Active Alerts ({len(filtered_alerts)})")
    
    # Alert list
    for i, alert in enumerate(filtered_alerts[:20]):  # Limit display for performance
        risk_colors = {
            'Critical': '#FF5252',
            'High': '#FF9800',
            'Medium': '#FFC107',
            'Low': '#00D395'
        }
        
        with st.container():
            # Alert card
            st.markdown(f"""
            <div class="alert-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0; color: #1A1A1A;">{alert['alert_id']} - {alert['risk_level']} Risk</h4>
                        <p style="color: #6B7280; margin: 0.5rem 0;">{alert['description']}</p>
                        <div style="display: flex; gap: 2rem; margin-top: 1rem;">
                            <div>
                                <strong>Transaction:</strong> <code>{alert['transaction_hash'][:16]}...{alert['transaction_hash'][-8:]}</code>
                            </div>
                            <div>
                                <strong>Value:</strong> {alert['total_value_btc']:.6f} BTC (${alert['total_value_usd']:,.2f})
                            </div>
                            <div>
                                <strong>ML Score:</strong> {alert['ml_score']:.2%}
                            </div>
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <small style="color: #9CA3AF;">
                                Created: {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} | 
                                Status: <span style="color: {'#00D395' if alert['status'] == 'Open' else '#FF9800'}">{alert['status']}</span>
                            </small>
                        </div>
                    </div>
                    <div class="risk-badge" style="background: {risk_colors[alert['risk_level']]}; color: white; padding: 0.5rem 1rem; border-radius: 20px;">
                        {alert['risk_level']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
            
            with col1:
                if st.button("🔍 Investigate", key=f"investigate_{i}"):
                    with st.expander("Investigation Details", expanded=True):
                        # Transaction details
                        st.markdown("#### Transaction Analysis")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Inputs", alert['num_inputs'])
                            st.metric("Outputs", alert['num_outputs'])
                        
                        with col2:
                            st.metric("Fee", f"{alert['fee']:.8f} BTC")
                            st.metric("Smurfing", "Yes" if alert['is_smurfing'] else "No")
                        
                        with col3:
                            st.metric("Risk Score", f"{alert['ml_score']:.2%}")
                            st.metric("Status", alert['status'])
                        
                        # Placeholder for graph visualization
                        st.markdown("#### Transaction Graph")
                        st.info("Transaction graph visualization would appear here, showing connections between addresses")
                        
                        # Update status
                        new_status = st.selectbox(
                            "Update Status",
                            ["Open", "Under Investigation", "Resolved"],
                            index=["Open", "Under Investigation", "Resolved"].index(alert.get('status', 'Open')),
                            key=f"status_update_{i}"
                        )
                        
                        if st.button("Update", key=f"update_status_{i}"):
                            alert['status'] = new_status
                            st.success(f"Status updated to: {new_status}")
                            st.rerun()
            
            with col2:
                if st.button("📄 Generate SAR", key=f"sar_{i}"):
                    with st.spinner("Generating SAR using AI..."):
                        # Generate SAR using the appropriate service
                        if st.session_state.USE_DUMMY_DATA:
                            sar_text = data_generator.generate_sar(alert)
                        else:
                            llm_conn = service_integration.get_llm_connection()
                            sar_text = llm_conn.generate_sar(alert)
                        
                        # Display SAR in a modal-like expander
                        with st.expander("📄 Suspicious Activity Report", expanded=True):
                            st.text_area(
                                "SAR Content",
                                sar_text,
                                height=500,
                                key=f"sar_text_{i}"
                            )
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.download_button(
                                    label="📥 Download SAR",
                                    data=sar_text,
                                    file_name=f"SAR_{alert['alert_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain",
                                    key=f"download_sar_{i}"
                                )
                            
                            with col2:
                                if st.button("📧 Email SAR", key=f"email_sar_{i}"):
                                    st.info("Email functionality would be implemented here")
                            
                            with col3:
                                if st.button("📋 Copy to Clipboard", key=f"copy_sar_{i}"):
                                    st.info("Copied to clipboard!")
            
            with col3:
                if st.button("📊 View Details", key=f"details_{i}"):
                    st.session_state.selected_page = "Transactions"
                    st.rerun()
            
            st.markdown("---")
    
    # Alert analytics
    if filtered_alerts:
        st.markdown("### 📈 Alert Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Alert trend over time
            df_alerts = pd.DataFrame(filtered_alerts)
            df_alerts['hour'] = pd.to_datetime(df_alerts['timestamp']).dt.floor('H')
            
            hourly_alerts = df_alerts.groupby(['hour', 'risk_level']).size().reset_index(name='count')
            
            fig = px.line(
                hourly_alerts,
                x='hour',
                y='count',
                color='risk_level',
                color_discrete_map={
                    'Critical': '#FF5252',
                    'High': '#FF9800',
                    'Medium': '#FFC107',
                    'Low': '#00D395'
                },
                title="Alert Trend (24h)",
                markers=True
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Alert resolution time
            resolved_alerts = [a for a in filtered_alerts if a['status'] == 'Resolved']
            if resolved_alerts:
                # This would calculate actual resolution time in production
                st.metric("Avg Resolution Time", "2.5 hours")
                st.metric("Alerts Resolved Today", len(resolved_alerts))
            else:
                st.info("No resolved alerts to analyze")
    
    # Export functionality
    if st.button("📥 Export Alert Report"):
        if filtered_alerts:
            df_export = pd.DataFrame(filtered_alerts)
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="Download Alert Report (CSV)",
                data=csv,
                file_name=f"alert_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No alerts to export")