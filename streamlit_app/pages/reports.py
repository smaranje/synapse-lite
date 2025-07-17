"""
Reports Page for Synapse-Lite
Report generation and viewing capabilities
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

class ReportsPage:
    """Reports page implementation"""
    
    def __init__(self, app_state):
        self.app_state = app_state
    
    def render(self):
        """Render the reports page"""
        self._render_reports_header()
        self._render_report_categories()
        self._render_report_generator()
        self._render_recent_reports()
    
    def _render_reports_header(self):
        """Render reports page header"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("## 📋 Reports & Analytics")
            st.markdown("Generate comprehensive reports for compliance, analysis, and stakeholder communication")
        
        with col2:
            if st.button("📊 Quick Report", use_container_width=True):
                self._generate_quick_report()
        
        with col3:
            if st.button("📁 Report Library", use_container_width=True):
                self._show_report_library()
    
    def _render_report_categories(self):
        """Render different report categories"""
        st.markdown("### 📂 Report Categories")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📈 Executive Summary", use_container_width=True, key="exec_summary"):
                self._generate_executive_summary()
        
        with col2:
            if st.button("🔍 Investigation Report", use_container_width=True, key="investigation"):
                self._generate_investigation_report()
        
        with col3:
            if st.button("⚖️ Compliance Report", use_container_width=True, key="compliance"):
                self._generate_compliance_report()
        
        with col4:
            if st.button("📊 Analytics Report", use_container_width=True, key="analytics"):
                self._generate_analytics_report()
    
    def _render_report_generator(self):
        """Render custom report generator"""
        st.markdown("### 🛠️ Custom Report Generator")
        
        with st.expander("📝 Create Custom Report", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                report_title = st.text_input("Report Title", placeholder="Enter report title...")
                report_type = st.selectbox(
                    "Report Type",
                    ["Executive Summary", "Technical Analysis", "Compliance Report", "Investigation Summary", "Custom"]
                )
                date_range = st.selectbox(
                    "Date Range", 
                    ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days", "Custom Range"]
                )
            
            with col2:
                include_charts = st.checkbox("Include Charts", value=True)
                include_raw_data = st.checkbox("Include Raw Data", value=False)
                format_type = st.selectbox("Output Format", ["PDF", "HTML", "Excel", "CSV"])
                
                recipients = st.text_input("Email Recipients (comma-separated)", placeholder="email1@example.com, email2@example.com")
            
            # Report sections
            st.markdown("**Report Sections:**")
            sections_col1, sections_col2 = st.columns(2)
            
            with sections_col1:
                include_overview = st.checkbox("System Overview", value=True)
                include_transactions = st.checkbox("Transaction Analysis", value=True)
                include_alerts = st.checkbox("Alert Summary", value=True)
            
            with sections_col2:
                include_risk = st.checkbox("Risk Assessment", value=True)
                include_geographic = st.checkbox("Geographic Analysis", value=False)
                include_recommendations = st.checkbox("Recommendations", value=True)
            
            if st.button("🚀 Generate Report", type="primary"):
                self._create_custom_report(
                    report_title, report_type, date_range, include_charts, 
                    include_raw_data, format_type, recipients
                )
    
    def _render_recent_reports(self):
        """Render list of recent reports"""
        st.markdown("### 📄 Recent Reports")
        
        # Mock recent reports data
        recent_reports = [
            {
                "title": "Daily Fraud Summary - December 2024",
                "type": "Executive Summary",
                "generated": "2024-12-08 09:30",
                "status": "Completed",
                "format": "PDF",
                "size": "2.3 MB"
            },
            {
                "title": "Weekly Risk Analysis Report",
                "type": "Analytics Report", 
                "generated": "2024-12-07 16:45",
                "status": "Completed",
                "format": "HTML",
                "size": "1.8 MB"
            },
            {
                "title": "Compliance Audit Report Q4",
                "type": "Compliance Report",
                "generated": "2024-12-06 11:20",
                "status": "In Progress",
                "format": "PDF",
                "size": "4.1 MB"
            },
            {
                "title": "Investigation Case Summary - CASE-45821",
                "type": "Investigation Report",
                "generated": "2024-12-05 14:15",
                "status": "Completed",
                "format": "PDF",
                "size": "3.7 MB"
            }
        ]
        
        # Display reports table
        for i, report in enumerate(recent_reports):
            status_color = {
                "Completed": "var(--success)",
                "In Progress": "var(--warning)",
                "Failed": "var(--error)"
            }.get(report["status"], "var(--secondary-text)")
            
            st.markdown(f"""
                <div class="metric-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: var(--primary-text); margin-bottom: 0.25rem;">
                                📊 {report['title']}
                            </div>
                            <div style="font-size: 0.875rem; color: var(--secondary-text);">
                                {report['type']} • Generated: {report['generated']}
                            </div>
                        </div>
                        <div style="text-align: right; margin-left: 1rem;">
                            <div style="margin-bottom: 0.5rem;">
                                <span style="background: {status_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                                    {report['status']}
                                </span>
                            </div>
                            <div style="font-size: 0.75rem; color: var(--secondary-text);">
                                {report['format']} • {report['size']}
                            </div>
                        </div>
                        <div style="margin-left: 1rem;">
                            <button style="background: var(--accent-blue); color: white; border: none; border-radius: 6px; padding: 0.5rem 1rem; font-size: 0.75rem; cursor: pointer; margin-right: 0.5rem;">
                                📥 Download
                            </button>
                            <button style="background: var(--secondary-bg); color: var(--primary-text); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.5rem 1rem; font-size: 0.75rem; cursor: pointer;">
                                👁️ View
                            </button>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    def _generate_executive_summary(self):
        """Generate executive summary report"""
        st.markdown("#### 📈 Executive Summary Report")
        
        from data.data_service import DataService
        data_service = DataService()
        
        # Get summary data
        transaction_stats = data_service.get_transaction_statistics()
        alert_stats = data_service.get_alert_statistics()
        system_metrics = data_service.get_system_metrics()
        reports_data = data_service.get_reports_data()
        
        daily_summary = reports_data['daily_summary']
        
        # Executive Summary Content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("##### Key Performance Indicators")
            
            # KPI metrics
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            
            with kpi_col1:
                st.metric(
                    "Daily Transactions",
                    f"{daily_summary['total_transactions']:,}",
                    delta="+5.2%"
                )
            
            with kpi_col2:
                st.metric(
                    "Total Volume",
                    f"${daily_summary['total_volume_usd']:,.0f}",
                    delta="+12.8%"
                )
            
            with kpi_col3:
                st.metric(
                    "Detection Accuracy",
                    f"{daily_summary['processing_accuracy']:.1f}%",
                    delta="+0.3%"
                )
            
            # Risk summary
            st.markdown("##### Risk Assessment Summary")
            
            risk_level = "Medium"
            risk_color = "var(--warning)"
            if alert_stats.get('high_risk_alerts', 0) > 10:
                risk_level = "High"
                risk_color = "var(--error)"
            elif alert_stats.get('high_risk_alerts', 0) < 3:
                risk_level = "Low"
                risk_color = "var(--success)"
            
            st.markdown(f"""
                <div class="alert-card" style="border-left-color: {risk_color};">
                    <strong>Overall Risk Level: {risk_level}</strong><br>
                    <p>Current risk assessment based on transaction patterns, alert frequency, and historical data analysis.</p>
                    <ul>
                        <li>High-risk alerts: {alert_stats.get('high_risk_alerts', 0)}</li>
                        <li>Active investigations: {alert_stats.get('active_alerts', 0)}</li>
                        <li>Resolution rate: {alert_stats.get('resolution_rate', 0):.1f}%</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # System health summary
            st.markdown("##### System Health")
            
            uptime = daily_summary['system_uptime']
            uptime_color = "var(--success)" if uptime > 99 else "var(--warning)"
            
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">System Uptime</div>
                    <div class="metric-value" style="color: {uptime_color};">{uptime:.2f}%</div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Blocked Amount</div>
                    <div class="metric-value">${daily_summary['blocked_amount_usd']:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Recommendations
            st.markdown("##### Recommendations")
            st.markdown("""
                1. **Alert Review**: Priority review of 3 high-risk alerts
                2. **System Optimization**: Monitor queue performance during peak hours
                3. **Model Tuning**: Consider adjusting threshold for geographic anomaly detection
                4. **Training**: Schedule team training on new investigation procedures
            """)
        
        # Generate report button
        if st.button("📄 Generate Full Executive Report"):
            st.success("Executive summary report generated successfully!")
            st.info("Report would be available for download in PDF format")
    
    def _generate_investigation_report(self):
        """Generate investigation report"""
        st.markdown("#### 🔍 Investigation Report")
        
        from data.data_service import DataService
        data_service = DataService()
        cases = data_service.get_investigation_cases()
        
        # Case selection
        case_titles = [f"{case['id']} - {case['title']}" for case in cases]
        selected_case_index = st.selectbox("Select Investigation Case", range(len(case_titles)), format_func=lambda x: case_titles[x])
        
        if cases:
            selected_case = cases[selected_case_index]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("##### Case Summary")
                st.markdown(f"**Case ID:** {selected_case['id']}")
                st.markdown(f"**Title:** {selected_case['title']}")
                st.markdown(f"**Status:** {selected_case['status'].replace('_', ' ').title()}")
                st.markdown(f"**Priority:** {selected_case['priority'].title()}")
                st.markdown(f"**Description:** {selected_case['description']}")
                
                st.markdown("##### Investigation Timeline")
                st.markdown(f"- **Created:** {selected_case['created_at']}")
                st.markdown(f"- **Last Activity:** {selected_case['last_activity']}")
                st.markdown(f"- **Assigned To:** {selected_case['assigned_to']}")
                
                st.markdown("##### Evidence Summary")
                st.markdown(f"- **Related Addresses:** {len(selected_case['related_addresses'])}")
                st.markdown(f"- **Related Transactions:** {selected_case['related_transactions']}")
                st.markdown(f"- **Evidence Items:** {selected_case['evidence_count']}")
            
            with col2:
                st.markdown("##### Case Metrics")
                
                st.metric(
                    "Estimated Value",
                    f"${selected_case['estimated_amount_usd']:,.2f}"
                )
                
                # Case priority visualization
                priority_score = {"low": 25, "medium": 50, "high": 75, "urgent": 100}[selected_case['priority']]
                st.progress(priority_score / 100, text=f"Priority: {selected_case['priority'].title()}")
                
                # Tags
                if selected_case.get('tags'):
                    st.markdown("**Tags:**")
                    for tag in selected_case['tags']:
                        st.markdown(f"- {tag}")
        
        if st.button("📄 Generate Investigation Report"):
            st.success("Investigation report generated successfully!")
    
    def _generate_compliance_report(self):
        """Generate compliance report"""
        st.markdown("#### ⚖️ Compliance Report")
        
        from data.data_service import DataService
        data_service = DataService()
        reports_data = data_service.get_reports_data()
        compliance_report = reports_data['compliance_report']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Regulatory Compliance")
            
            # Compliance metrics
            compliance_score = 94.5
            st.progress(compliance_score / 100, text=f"Compliance Score: {compliance_score}%")
            
            st.metric("SAR Reports", compliance_report['suspicious_activity_reports'])
            st.metric("CTR Reports", compliance_report['currency_transaction_reports'])
            st.metric("KYC Checks", compliance_report['kyc_checks_performed'])
        
        with col2:
            st.markdown("##### Audit Findings")
            
            st.metric("AML Flags", compliance_report['aml_flags'], delta="-5")
            st.metric("Regulatory Queries", compliance_report['regulatory_queries'])
            st.metric("Audit Findings", compliance_report['audit_findings'])
            
            if compliance_report['audit_findings'] == 0:
                st.success("✅ No audit findings this period")
            else:
                st.warning(f"⚠️ {compliance_report['audit_findings']} audit findings require attention")
        
        # Compliance summary
        st.markdown("##### Compliance Summary")
        st.markdown(f"""
            **Report Period:** {compliance_report['report_date']}
            
            **Key Highlights:**
            - All regulatory reporting requirements met on time
            - KYC completion rate: 98.7%
            - AML monitoring coverage: 100%
            - Staff training completion: {compliance_report['compliance_training_completed']} employees
            
            **Action Items:**
            - Review and update customer risk assessments
            - Complete quarterly compliance training
            - Prepare for upcoming regulatory examination
        """)
        
        if st.button("📄 Generate Compliance Report"):
            st.success("Compliance report generated successfully!")
    
    def _generate_analytics_report(self):
        """Generate analytics report"""
        st.markdown("#### 📊 Analytics Report")
        
        from data.data_service import DataService
        data_service = DataService()
        
        # Create analytics visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Transaction volume chart
            volume_data = data_service.get_transaction_volume_data('30d')
            
            fig = px.line(
                x=volume_data['dates'],
                y=volume_data['volumes'],
                title="30-Day Transaction Volume Trend",
                labels={'x': 'Date', 'y': 'Volume (USD)'}
            )
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Risk distribution
            risk_analytics = data_service.get_risk_analytics()
            risk_dist = risk_analytics['risk_distribution']
            
            fig = px.pie(
                values=list(risk_dist.values()),
                names=list(risk_dist.keys()),
                title="Risk Distribution",
                color_discrete_sequence=['#00d924', '#ff9500', '#ff4757', '#dc143c']
            )
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Analytics insights
        st.markdown("##### Key Analytics Insights")
        
        insights_col1, insights_col2, insights_col3 = st.columns(3)
        
        with insights_col1:
            st.markdown("""
                **Volume Trends**
                - 15% increase in daily volume
                - Peak hours: 14:00-16:00 UTC
                - Geographic concentration in North America
            """)
        
        with insights_col2:
            st.markdown("""
                **Risk Patterns**
                - Velocity anomalies most common
                - Geographic risk factors increasing
                - Model accuracy at 96.8%
            """)
        
        with insights_col3:
            st.markdown("""
                **Performance**
                - Processing latency: 35ms avg
                - Detection rate: 94.2%
                - False positive rate: 3.1%
            """)
        
        if st.button("📄 Generate Analytics Report"):
            st.success("Analytics report generated successfully!")
    
    def _generate_quick_report(self):
        """Generate a quick summary report"""
        st.info("Generating quick summary report...")
        
    def _show_report_library(self):
        """Show report library/archive"""
        st.info("Report library would show archived reports here")
    
    def _create_custom_report(self, title, report_type, date_range, include_charts, include_raw_data, format_type, recipients):
        """Create a custom report based on user specifications"""
        st.success(f"Custom report '{title}' is being generated...")
        st.info(f"Report will be available in {format_type} format")
        
        if recipients:
            st.info(f"Report will be emailed to: {recipients}")