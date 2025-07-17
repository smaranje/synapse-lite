"""
Alerts Page for Synapse-Lite
Fraud alert management and investigation
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

class AlertsPage:
    """Alerts page implementation"""
    
    def __init__(self, app_state):
        self.app_state = app_state
    
    def render(self):
        """Render the alerts page"""
        self._render_alert_summary()
        self._render_alert_filters()
        self._render_alerts_list()
        self._render_alert_analytics()
    
    def _render_alert_summary(self):
        """Render alert summary metrics"""
        st.markdown("## 🚨 Fraud Alerts Management")
        
        from data.data_service import DataService
        data_service = DataService()
        alert_stats = data_service.get_alert_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Alerts",
                alert_stats.get('total_alerts', 0),
                help="Total alerts in the system"
            )
        
        with col2:
            st.metric(
                "Active Alerts",
                alert_stats.get('active_alerts', 0),
                delta=f"{alert_stats.get('high_risk_alerts', 0)} high risk",
                help="Currently active alerts requiring attention"
            )
        
        with col3:
            st.metric(
                "Resolution Rate",
                f"{alert_stats.get('resolution_rate', 0):.1f}%",
                delta=f"{alert_stats.get('resolved_alerts', 0)} resolved",
                help="Percentage of alerts resolved"
            )
        
        with col4:
            pending = alert_stats.get('pending_alerts', 0)
            st.metric(
                "Pending Review",
                pending,
                delta="⚠️" if pending > 10 else "✅",
                help="Alerts pending investigation"
            )
    
    def _render_alert_filters(self):
        """Render alert filtering controls"""
        with st.expander("🔍 Filter Alerts", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                severity_filter = st.selectbox(
                    "Severity",
                    ["all", "low", "medium", "high", "critical"]
                )
            
            with col2:
                status_filter = st.selectbox(
                    "Status", 
                    ["all", "active", "investigating", "resolved", "false_positive"]
                )
            
            with col3:
                time_filter = st.selectbox(
                    "Time Range",
                    ["24 hours", "7 days", "30 days", "All time"]
                )
            
            with col4:
                type_filter = st.selectbox(
                    "Alert Type",
                    ["all", "Suspicious Pattern", "High-Risk Transaction", "Velocity Threshold", "Geographic Anomaly"]
                )
        
        # Apply filters
        self._apply_alert_filters(severity_filter, status_filter, time_filter, type_filter)
    
    def _apply_alert_filters(self, severity, status, time_range, alert_type):
        """Apply filters to alerts"""
        alerts = self.app_state.get_alerts_data()
        
        filtered_alerts = []
        for alert in alerts:
            # Apply filters
            if severity != "all" and alert.get('severity') != severity:
                continue
            
            if status != "all" and alert.get('status') != status:
                continue
            
            if alert_type != "all" and alert_type not in alert.get('type', ''):
                continue
            
            # Time filter
            if time_range != "All time":
                alert_time = datetime.fromisoformat(alert.get('timestamp', ''))
                now = datetime.now()
                
                if time_range == "24 hours" and (now - alert_time).days >= 1:
                    continue
                elif time_range == "7 days" and (now - alert_time).days >= 7:
                    continue
                elif time_range == "30 days" and (now - alert_time).days >= 30:
                    continue
            
            filtered_alerts.append(alert)
        
        st.session_state.filtered_alerts = filtered_alerts
    
    def _render_alerts_list(self):
        """Render the list of alerts"""
        st.markdown("### Alert Details")
        
        filtered_alerts = st.session_state.get('filtered_alerts', [])
        
        if filtered_alerts:
            # Create tabs for different views
            tab1, tab2 = st.tabs(["📋 List View", "📊 Card View"])
            
            with tab1:
                self._render_alerts_table(filtered_alerts)
            
            with tab2:
                self._render_alerts_cards(filtered_alerts)
        else:
            st.info("No alerts match the current filters.")
    
    def _render_alerts_table(self, alerts):
        """Render alerts in table format"""
        # Convert to DataFrame
        df_data = []
        for alert in alerts:
            timestamp = datetime.fromisoformat(alert.get('timestamp', ''))
            df_data.append({
                'ID': alert.get('id', ''),
                'Type': alert.get('type', ''),
                'Severity': alert.get('severity', '').title(),
                'Status': alert.get('status', '').title(),
                'Risk Score': alert.get('risk_score', 0),
                'Amount': f"${alert.get('total_amount_usd', 0):,.2f}",
                'Country': alert.get('country', 'Unknown'),
                'Created': timestamp.strftime('%Y-%m-%d %H:%M'),
                'Assigned To': alert.get('assigned_to', 'Unassigned')
            })
        
        df = pd.DataFrame(df_data)
        
        # Display with selection
        selected_indices = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Show selected alert details
        if selected_indices and len(selected_indices.selection.rows) > 0:
            selected_idx = selected_indices.selection.rows[0]
            selected_alert = alerts[selected_idx]
            self._render_alert_details(selected_alert)
    
    def _render_alerts_cards(self, alerts):
        """Render alerts in card format"""
        for i, alert in enumerate(alerts[:10]):  # Show first 10 alerts
            severity = alert.get('severity', 'low')
            severity_colors = {
                'low': 'var(--info)',
                'medium': 'var(--warning)',
                'high': 'var(--error)',
                'critical': 'var(--accent-red)'
            }
            
            timestamp = datetime.fromisoformat(alert.get('timestamp', ''))
            time_str = timestamp.strftime('%Y-%m-%d %H:%M')
            
            # Create expandable alert card
            with st.expander(f"{alert.get('type', 'Unknown Alert')} - {severity.title()} Severity"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {alert.get('description', 'No description available')}")
                    st.markdown(f"**Risk Score:** {alert.get('risk_score', 0)}/100")
                    st.markdown(f"**Affected Addresses:** {len(alert.get('affected_addresses', []))}")
                    st.markdown(f"**Transaction Count:** {alert.get('transaction_count', 0)}")
                    st.markdown(f"**Country:** {alert.get('country', 'Unknown')}")
                
                with col2:
                    st.markdown(f"**Status:** {alert.get('status', 'unknown').title()}")
                    st.markdown(f"**Created:** {time_str}")
                    st.markdown(f"**Assigned To:** {alert.get('assigned_to', 'Unassigned')}")
                    st.markdown(f"**Amount:** ${alert.get('total_amount_usd', 0):,.2f}")
                    
                    # Action buttons
                    if st.button(f"Investigate", key=f"investigate_{i}"):
                        self._start_investigation(alert)
                    
                    if st.button(f"Mark Resolved", key=f"resolve_{i}"):
                        self._resolve_alert(alert)
    
    def _render_alert_details(self, alert):
        """Render detailed view of selected alert"""
        st.markdown("#### Alert Details")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Alert Information**")
            st.json({
                'ID': alert.get('id'),
                'Type': alert.get('type'),
                'Description': alert.get('description'),
                'Risk Score': alert.get('risk_score'),
                'Status': alert.get('status'),
                'Severity': alert.get('severity'),
                'Created By': alert.get('created_by'),
                'Investigation Notes': alert.get('investigation_notes')
            })
        
        with col2:
            st.markdown("**Actions**")
            
            # Status update
            new_status = st.selectbox(
                "Update Status",
                ["active", "investigating", "resolved", "false_positive"],
                index=["active", "investigating", "resolved", "false_positive"].index(alert.get('status', 'active'))
            )
            
            if st.button("Update Status"):
                self.app_state.update_alert_status(alert.get('id'), new_status)
                st.success(f"Alert status updated to {new_status}")
                st.rerun()
            
            # Assignment
            assignee = st.selectbox(
                "Assign To",
                ["Unassigned", "Analyst A", "Analyst B", "Senior Investigator", "Team Lead"]
            )
            
            if st.button("Assign Alert"):
                st.success(f"Alert assigned to {assignee}")
            
            # Create investigation
            if st.button("Create Investigation"):
                self._create_investigation_from_alert(alert)
    
    def _render_alert_analytics(self):
        """Render alert analytics and trends"""
        st.markdown("### Alert Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_severity_distribution()
        
        with col2:
            self._render_alert_trends()
    
    def _render_severity_distribution(self):
        """Render alert severity distribution"""
        alerts = st.session_state.get('filtered_alerts', [])
        
        if alerts:
            severity_counts = {}
            for alert in alerts:
                severity = alert.get('severity', 'unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            fig = px.pie(
                values=list(severity_counts.values()),
                names=list(severity_counts.keys()),
                title="Alert Severity Distribution",
                color_discrete_map={
                    'low': '#00d924',
                    'medium': '#ff9500',
                    'high': '#ff4757',
                    'critical': '#dc143c'
                }
            )
            
            fig.update_layout(
                template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_alert_trends(self):
        """Render alert trends over time"""
        alerts = st.session_state.get('filtered_alerts', [])
        
        if alerts:
            # Group by day
            daily_counts = {}
            for alert in alerts:
                timestamp = datetime.fromisoformat(alert.get('timestamp', ''))
                day_key = timestamp.strftime('%Y-%m-%d')
                daily_counts[day_key] = daily_counts.get(day_key, 0) + 1
            
            # Sort by date
            sorted_days = sorted(daily_counts.keys())
            counts = [daily_counts[day] for day in sorted_days]
            
            fig = go.Figure(data=go.Scatter(
                x=sorted_days,
                y=counts,
                mode='lines+markers',
                name='Daily Alerts',
                line=dict(color='#ff4757', width=3)
            ))
            
            fig.update_layout(
                title="Alert Trends",
                xaxis_title="Date",
                yaxis_title="Alert Count",
                template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _start_investigation(self, alert):
        """Start investigation for an alert"""
        st.success(f"Investigation started for alert {alert.get('id')}")
        # Update alert status
        self.app_state.update_alert_status(alert.get('id'), 'investigating')
    
    def _resolve_alert(self, alert):
        """Mark alert as resolved"""
        st.success(f"Alert {alert.get('id')} marked as resolved")
        self.app_state.update_alert_status(alert.get('id'), 'resolved')
    
    def _create_investigation_from_alert(self, alert):
        """Create investigation case from alert"""
        case_data = {
            'title': f"Investigation: {alert.get('type')}",
            'description': f"Investigation created from alert {alert.get('id')}: {alert.get('description')}",
            'severity': alert.get('severity', 'medium'),
            'related_transactions': alert.get('affected_addresses', [])
        }
        
        new_case = self.app_state.add_investigation_case(case_data)
        st.success(f"Investigation case created from alert")