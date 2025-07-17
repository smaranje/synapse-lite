# Alerts page module

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_generator import generate_alert_data, format_hash
from styling import create_risk_badge
from charts import create_alert_type_distribution

def render_alerts():
    """Render the security alerts management page"""
    st.title("🚨 Security Alerts")
    st.markdown("### Real-time Fraud Detection Alerts")
    
    # Generate alert data
    alert_df = generate_alert_data(50)
    
    # Control panel
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search alerts", placeholder="Alert ID, type, or description...")
    
    with col2:
        severity_filter = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])
    
    with col3:
        status_filter = st.selectbox("Status", ["All", "Open", "Investigating", "Resolved", "False Positive"])
    
    with col4:
        source_filter = st.selectbox("Source", ["All", "ML Model", "Rule Engine", "Manual Review", "External API"])
    
    # Refresh button
    if st.button("🔄 Refresh Alerts", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Apply filters
    filtered_alerts = alert_df.copy()
    
    if severity_filter != "All":
        filtered_alerts = filtered_alerts[filtered_alerts["Severity"] == severity_filter]
    
    if status_filter != "All":
        filtered_alerts = filtered_alerts[filtered_alerts["Status"] == status_filter]
        
    if source_filter != "All":
        filtered_alerts = filtered_alerts[filtered_alerts["Source"] == source_filter]
    
    if search_term:
        search_mask = (
            filtered_alerts["ID"].str.contains(search_term, case=False, na=False) |
            filtered_alerts["Type"].str.contains(search_term, case=False, na=False) |
            filtered_alerts["Description"].str.contains(search_term, case=False, na=False)
        )
        filtered_alerts = filtered_alerts[search_mask]
    
    st.markdown("---")
    
    # Alert summary
    st.markdown("## Alert Summary")
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        open_alerts = len(filtered_alerts[filtered_alerts["Status"] == "Open"])
        st.metric("Open Alerts", open_alerts, "🔴" if open_alerts > 10 else "🟢")
    
    with summary_col2:
        critical_alerts = len(filtered_alerts[filtered_alerts["Severity"] == "Critical"])
        st.metric("Critical Alerts", critical_alerts, "⚠️" if critical_alerts > 0 else "✅")
    
    with summary_col3:
        investigating = len(filtered_alerts[filtered_alerts["Status"] == "Investigating"])
        st.metric("Under Investigation", investigating)
    
    with summary_col4:
        resolved_today = len(filtered_alerts[filtered_alerts["Status"] == "Resolved"])
        st.metric("Resolved Today", resolved_today, "+5")
    
    # Alert distribution chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Alert Type Distribution")
        fig = create_alert_type_distribution()
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Severity Breakdown")
        severity_counts = filtered_alerts['Severity'].value_counts()
        for severity, count in severity_counts.items():
            percentage = (count / len(filtered_alerts)) * 100 if len(filtered_alerts) > 0 else 0
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background: white; border-radius: 8px; margin: 0.5rem 0; border: 1px solid #f0f3f7;">
                <span>{create_risk_badge(severity)} {severity}</span>
                <span style="font-weight: 600;">{count} ({percentage:.1f}%)</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Alert list
    st.markdown("## Active Alerts")
    
    if len(filtered_alerts) > 0:
        # Sort by severity and timestamp
        severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        filtered_alerts['severity_rank'] = filtered_alerts['Severity'].map(severity_order)
        filtered_alerts = filtered_alerts.sort_values(['severity_rank', 'Timestamp'], ascending=[True, False])
        
        for idx, alert in filtered_alerts.head(20).iterrows():  # Limit to 20 for performance
            severity_class = alert['Severity'].lower()
            
            # Determine status color
            status_colors = {
                "Open": "#dc2626",
                "Investigating": "#ea580c", 
                "Resolved": "#059669",
                "False Positive": "#6b7280"
            }
            status_color = status_colors.get(alert['Status'], "#6b7280")
            
            # Determine priority icon
            priority_icons = {
                "Critical": "🔴",
                "High": "🟠", 
                "Medium": "🟡",
                "Low": "🟢"
            }
            priority_icon = priority_icons.get(alert['Severity'], "⚪")
            
            st.markdown(f"""
            <div class="alert-card {severity_class}">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.2rem;">{priority_icon}</span>
                            <span style="font-weight: 600; font-size: 1.1rem; color: #1a1a1a;">
                                {alert['ID']}
                            </span>
                            <span>{create_risk_badge(alert['Severity'])}</span>
                        </div>
                        
                        <div style="font-weight: 600; color: #374151; margin-bottom: 0.5rem;">
                            {alert['Type']}
                        </div>
                        
                        <div style="color: #6b7280; margin-bottom: 0.75rem; line-height: 1.4;">
                            {alert['Description']}
                        </div>
                        
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; font-size: 0.875rem;">
                            <div>
                                <span style="color: #6b7280;">Transaction:</span><br>
                                <span style="font-family: monospace; font-weight: 500;">{format_hash(alert['Transaction Hash'], 6)}</span>
                            </div>
                            <div>
                                <span style="color: #6b7280;">Amount:</span><br>
                                <span style="font-weight: 600; color: #0052ff;">₿{alert['Amount']:.4f}</span>
                            </div>
                            <div>
                                <span style="color: #6b7280;">Risk Score:</span><br>
                                <span style="font-weight: 600;">{alert['Risk Score']}%</span>
                            </div>
                            <div>
                                <span style="color: #6b7280;">Source:</span><br>
                                <span style="font-weight: 500;">{alert['Source']}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: right; min-width: 120px;">
                        <div style="margin-bottom: 0.5rem;">
                            <span style="
                                display: inline-block;
                                padding: 0.25rem 0.75rem;
                                border-radius: 20px;
                                font-size: 0.75rem;
                                font-weight: 600;
                                background: {status_color};
                                color: white;
                            ">{alert['Status']}</span>
                        </div>
                        
                        <div style="font-size: 0.875rem; color: #6b7280; margin-bottom: 0.5rem;">
                            {alert['Timestamp'].strftime('%m/%d %H:%M')}
                        </div>
                        
                        <div style="font-size: 0.75rem; color: #6b7280;">
                            Assigned: {alert['Assigned To']}
                        </div>
                        
                        <div style="margin-top: 1rem; display: flex; flex-direction: column; gap: 0.5rem;">
                            <button style="
                                background: #0052ff;
                                color: white;
                                border: none;
                                border-radius: 6px;
                                padding: 0.5rem 1rem;
                                font-size: 0.75rem;
                                font-weight: 500;
                                cursor: pointer;
                                width: 100%;
                            ">Investigate</button>
                            
                            <button style="
                                background: #059669;
                                color: white;
                                border: none;
                                border-radius: 6px;
                                padding: 0.5rem 1rem;
                                font-size: 0.75rem;
                                font-weight: 500;
                                cursor: pointer;
                                width: 100%;
                            ">Mark Resolved</button>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.info("No alerts match your current filters.")
    
    # Alert management tools
    st.markdown("---")
    st.markdown("## Alert Management")
    
    tool_col1, tool_col2, tool_col3 = st.columns(3)
    
    with tool_col1:
        st.markdown("### Bulk Actions")
        if st.button("Mark All as Reviewed"):
            st.success("All visible alerts marked as reviewed")
        if st.button("Export to CSV"):
            st.success("Alert data exported successfully")
    
    with tool_col2:
        st.markdown("### Alert Rules")
        st.selectbox("Rule Template", ["High Volume", "Unusual Pattern", "Geographic Risk", "Custom"])
        if st.button("Create New Rule"):
            st.info("Rule creation interface would open here")
    
    with tool_col3:
        st.markdown("### Notification Settings")
        st.checkbox("Email notifications", value=True)
        st.checkbox("SMS for critical alerts", value=True)
        st.selectbox("Notification frequency", ["Immediate", "Every 5 min", "Hourly"])