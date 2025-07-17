# Settings page module

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def render_settings():
    """Render the system configuration settings page"""
    st.title("⚙️ Settings")
    st.markdown("### System Configuration & Preferences")
    
    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔧 General", "🔒 Security", "📊 Detection", "🔔 Alerts", "💾 Data"])
    
    with tab1:
        st.markdown("## General Settings")
        
        # Display preferences
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Display Preferences")
            
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=0)
            refresh_rate = st.slider("Auto-refresh Rate (seconds)", 5, 300, 30)
            show_animations = st.checkbox("Enable animations", value=True)
            compact_view = st.checkbox("Compact view mode", value=False)
            
            st.markdown("### Language & Localization")
            language = st.selectbox("Language", ["English", "Spanish", "French", "German"], index=0)
            timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "CET"], index=0)
            date_format = st.selectbox("Date Format", ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"], index=0)
        
        with col2:
            st.markdown("### Performance Settings")
            
            max_transactions = st.slider("Max transactions to display", 50, 1000, 200)
            cache_duration = st.slider("Cache duration (minutes)", 1, 60, 5)
            enable_lazy_loading = st.checkbox("Enable lazy loading", value=True)
            
            st.markdown("### User Preferences")
            default_page = st.selectbox("Default page", ["Dashboard", "Transactions", "Alerts", "Analytics"], index=0)
            sidebar_collapsed = st.checkbox("Sidebar collapsed by default", value=False)
            
        # Save settings
        if st.button("💾 Save General Settings", type="primary"):
            st.success("General settings saved successfully!")
    
    with tab2:
        st.markdown("## Security Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Authentication")
            
            session_timeout = st.selectbox("Session timeout", ["15 min", "30 min", "1 hour", "4 hours", "8 hours"], index=1)
            require_2fa = st.checkbox("Require two-factor authentication", value=False)
            password_expiry = st.selectbox("Password expiry", ["Never", "30 days", "60 days", "90 days"], index=2)
            
            st.markdown("### Access Control")
            admin_email = st.text_input("Admin Email", value="admin@company.com")
            max_failed_logins = st.slider("Max failed login attempts", 3, 10, 5)
            lockout_duration = st.slider("Account lockout duration (minutes)", 5, 60, 15)
        
        with col2:
            st.markdown("### API Security")
            
            api_key_expiry = st.selectbox("API key expiry", ["30 days", "90 days", "1 year", "Never"], index=1)
            rate_limiting = st.checkbox("Enable API rate limiting", value=True)
            if rate_limiting:
                rate_limit = st.slider("Requests per minute", 60, 1000, 300)
            
            st.markdown("### Audit & Logging")
            enable_audit_log = st.checkbox("Enable audit logging", value=True)
            log_level = st.selectbox("Log Level", ["INFO", "DEBUG", "WARNING", "ERROR"], index=0)
            retain_logs = st.selectbox("Log retention period", ["30 days", "90 days", "1 year", "2 years"], index=1)
        
        # Security status
        st.markdown("---")
        st.markdown("### Security Status")
        
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            st.markdown("""
            <div style="padding: 1rem; background: #f0fdf4; border-radius: 8px; border: 1px solid #bbf7d0;">
                <div style="color: #059669; font-weight: 600; margin-bottom: 0.5rem;">🔒 Security Score</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #059669;">94/100</div>
                <div style="font-size: 0.875rem; color: #16a34a;">Excellent</div>
            </div>
            """, unsafe_allow_html=True)
        
        with status_col2:
            st.markdown("""
            <div style="padding: 1rem; background: #fffbeb; border-radius: 8px; border: 1px solid #fed7aa;">
                <div style="color: #ea580c; font-weight: 600; margin-bottom: 0.5rem;">⚠️ Vulnerabilities</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #ea580c;">2</div>
                <div style="font-size: 0.875rem; color: #ea580c;">Needs attention</div>
            </div>
            """, unsafe_allow_html=True)
        
        with status_col3:
            st.markdown("""
            <div style="padding: 1rem; background: #eff6ff; border-radius: 8px; border: 1px solid #bfdbfe;">
                <div style="color: #0052ff; font-weight: 600; margin-bottom: 0.5rem;">🛡️ Last Scan</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #0052ff;">2h ago</div>
                <div style="font-size: 0.875rem; color: #0052ff;">Up to date</div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🔒 Save Security Settings", type="primary"):
            st.success("Security settings updated successfully!")
    
    with tab3:
        st.markdown("## Detection Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Risk Thresholds")
            
            critical_threshold = st.slider("Critical Risk Threshold (%)", 70, 100, 80)
            high_threshold = st.slider("High Risk Threshold (%)", 50, 90, 60)
            medium_threshold = st.slider("Medium Risk Threshold (%)", 20, 70, 40)
            
            st.markdown("### Detection Rules")
            enable_ml_detection = st.checkbox("Enable ML-based detection", value=True)
            enable_rule_engine = st.checkbox("Enable rule engine", value=True)
            enable_pattern_matching = st.checkbox("Enable pattern matching", value=True)
            
            st.markdown("### Transaction Limits")
            max_transaction_amount = st.number_input("Max transaction amount ($)", value=10000, min_value=0)
            daily_volume_limit = st.number_input("Daily volume limit ($)", value=50000, min_value=0)
        
        with col2:
            st.markdown("### Model Configuration")
            
            model_version = st.selectbox("Active Model Version", ["v2.1.3", "v2.1.2", "v2.0.8"], index=0)
            model_sensitivity = st.slider("Model Sensitivity", 0.1, 1.0, 0.7, 0.1)
            auto_retrain = st.checkbox("Enable automatic retraining", value=True)
            
            st.markdown("### Real-time Processing")
            processing_mode = st.selectbox("Processing Mode", ["Real-time", "Batch", "Hybrid"], index=0)
            batch_size = st.slider("Batch Size", 100, 10000, 1000)
            processing_timeout = st.slider("Processing Timeout (seconds)", 1, 30, 10)
            
            st.markdown("### False Positive Management")
            auto_dismiss_threshold = st.slider("Auto-dismiss threshold (%)", 0, 50, 15)
            whitelist_addresses = st.text_area("Whitelisted Addresses (one per line)", height=100)
        
        # Model performance metrics
        st.markdown("---")
        st.markdown("### Current Model Performance")
        
        perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
        
        with perf_col1:
            st.metric("Accuracy", "94.2%", "+1.3%")
        with perf_col2:
            st.metric("Precision", "91.8%", "+0.7%")
        with perf_col3:
            st.metric("Recall", "93.0%", "-0.2%")
        with perf_col4:
            st.metric("F1-Score", "92.4%", "+0.5%")
        
        if st.button("🎯 Save Detection Settings", type="primary"):
            st.success("Detection settings configured successfully!")
    
    with tab4:
        st.markdown("## Alert Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Notification Preferences")
            
            email_alerts = st.checkbox("Enable email alerts", value=True)
            if email_alerts:
                alert_email = st.text_input("Alert Email Address", value="alerts@company.com")
                email_frequency = st.selectbox("Email Frequency", ["Immediate", "Every 5 min", "Hourly", "Daily"], index=0)
            
            sms_alerts = st.checkbox("Enable SMS alerts", value=False)
            if sms_alerts:
                sms_number = st.text_input("SMS Number", placeholder="+1234567890")
                sms_critical_only = st.checkbox("SMS for critical alerts only", value=True)
            
            webhook_alerts = st.checkbox("Enable webhook notifications", value=False)
            if webhook_alerts:
                webhook_url = st.text_input("Webhook URL", placeholder="https://your-webhook.com/alerts")
        
        with col2:
            st.markdown("### Alert Rules")
            
            st.markdown("#### Critical Alerts")
            critical_immediate = st.checkbox("Immediate notification for critical alerts", value=True)
            critical_escalation = st.selectbox("Escalation after", ["5 min", "15 min", "30 min", "1 hour"], index=1)
            
            st.markdown("#### High Risk Alerts")
            high_risk_frequency = st.selectbox("High risk alert frequency", ["Immediate", "5 min", "15 min"], index=1)
            
            st.markdown("#### Alert Suppression")
            suppress_duplicates = st.checkbox("Suppress duplicate alerts", value=True)
            if suppress_duplicates:
                suppression_window = st.slider("Suppression window (minutes)", 1, 60, 10)
        
        # Alert statistics
        st.markdown("---")
        st.markdown("### Alert Statistics (Last 24h)")
        
        alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)
        
        with alert_col1:
            st.metric("Total Alerts", "127", "+15")
        with alert_col2:
            st.metric("Critical", "8", "+3")
        with alert_col3:
            st.metric("Resolved", "89", "+12")
        with alert_col4:
            st.metric("False Positives", "4", "-2")
        
        if st.button("🔔 Save Alert Settings", type="primary"):
            st.success("Alert settings updated successfully!")
    
    with tab5:
        st.markdown("## Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Data Sources")
            
            primary_source = st.selectbox("Primary Data Source", ["Neo4j Database", "PostgreSQL", "MongoDB"], index=0)
            backup_source = st.selectbox("Backup Data Source", ["None", "S3 Bucket", "Local Storage"], index=1)
            
            st.markdown("### Data Retention")
            transaction_retention = st.selectbox("Transaction Data Retention", ["30 days", "90 days", "1 year", "5 years"], index=2)
            alert_retention = st.selectbox("Alert Data Retention", ["90 days", "1 year", "2 years", "5 years"], index=1)
            log_retention = st.selectbox("Log Data Retention", ["30 days", "90 days", "1 year"], index=1)
            
            st.markdown("### Data Export")
            export_format = st.selectbox("Default Export Format", ["CSV", "JSON", "XML", "Parquet"], index=0)
            include_sensitive = st.checkbox("Include sensitive data in exports", value=False)
        
        with col2:
            st.markdown("### Database Configuration")
            
            st.text_input("Neo4j Connection String", value="bolt://neo4j:7687")
            st.text_input("Database Username", value="neo4j")
            st.text_input("Database Password", type="password", value="password")
            
            st.markdown("### Backup Settings")
            auto_backup = st.checkbox("Enable automatic backups", value=True)
            if auto_backup:
                backup_frequency = st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"], index=0)
                backup_location = st.text_input("Backup Location", value="/backups/")
            
            st.markdown("### Data Quality")
            enable_validation = st.checkbox("Enable data validation", value=True)
            remove_duplicates = st.checkbox("Automatically remove duplicates", value=True)
        
        # Storage statistics
        st.markdown("---")
        st.markdown("### Storage Statistics")
        
        storage_col1, storage_col2, storage_col3, storage_col4 = st.columns(4)
        
        with storage_col1:
            st.metric("Total Storage", "2.3 TB", "+120 GB")
        with storage_col2:
            st.metric("Transaction Data", "1.8 TB", "+95 GB")
        with storage_col3:
            st.metric("Alert Data", "245 GB", "+12 GB")
        with storage_col4:
            st.metric("Log Data", "378 GB", "+18 GB")
        
        # Data management actions
        st.markdown("---")
        st.markdown("### Data Management Actions")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("🔄 Backup Now"):
                st.success("Backup initiated successfully!")
        
        with action_col2:
            if st.button("🧹 Clean Old Data"):
                st.success("Data cleanup completed!")
        
        with action_col3:
            if st.button("📊 Generate Report"):
                st.success("Data usage report generated!")
        
        if st.button("💾 Save Data Settings", type="primary"):
            st.success("Data management settings saved successfully!")
    
    # Footer with system info
    st.markdown("---")
    st.markdown("### System Information")
    
    info_col1, info_col2, info_col3 = st.columns(3)
    
    with info_col1:
        st.markdown("""
        **Application Version:** v2.1.3  
        **Build Date:** 2024-07-17  
        **Environment:** Production
        """)
    
    with info_col2:
        st.markdown("""
        **Last Updated:** 2 hours ago  
        **Uptime:** 15 days, 3 hours  
        **Active Users:** 23
        """)
    
    with info_col3:
        st.markdown("""
        **Support:** support@company.com  
        **Documentation:** [View Docs](/)  
        **Status Page:** [System Status](/)
        """)