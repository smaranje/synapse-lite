"""
Settings Page for Synapse-Lite
Application configuration and user preferences
"""

import streamlit as st
import json
from datetime import datetime

class SettingsPage:
    """Settings page implementation"""
    
    def __init__(self, app_state):
        self.app_state = app_state
    
    def render(self):
        """Render the settings page"""
        self._render_settings_header()
        self._render_settings_tabs()
    
    def _render_settings_header(self):
        """Render settings page header"""
        st.markdown("## ⚙️ Settings & Configuration")
        st.markdown("Configure application preferences, system settings, and user options")
    
    def _render_settings_tabs(self):
        """Render settings organized in tabs"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎨 Appearance", 
            "🔔 Notifications", 
            "🔒 Security", 
            "⚙️ System", 
            "📊 Data"
        ])
        
        with tab1:
            self._render_appearance_settings()
        
        with tab2:
            self._render_notification_settings()
        
        with tab3:
            self._render_security_settings()
        
        with tab4:
            self._render_system_settings()
        
        with tab5:
            self._render_data_settings()
    
    def _render_appearance_settings(self):
        """Render appearance and UI settings"""
        st.markdown("### 🎨 Appearance Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Theme & Layout")
            
            # Theme selection
            current_theme = self.app_state.get_setting('theme', 'dark')
            theme = st.selectbox(
                "Color Theme",
                ["dark", "light"],
                index=0 if current_theme == 'dark' else 1,
                help="Choose between dark and light theme"
            )
            
            if theme != current_theme:
                self.app_state.set_setting('theme', theme)
                st.rerun()
            
            # Layout preferences
            compact_view = st.checkbox(
                "Compact View",
                value=self.app_state.get_setting('compact_view', False),
                help="Use compact layout to show more information"
            )
            self.app_state.set_setting('compact_view', compact_view)
            
            # Chart animations
            chart_animation = st.checkbox(
                "Chart Animations",
                value=self.app_state.get_setting('chart_animation', True),
                help="Enable smooth animations in charts and graphs"
            )
            self.app_state.set_setting('chart_animation', chart_animation)
        
        with col2:
            st.markdown("#### Display Options")
            
            # Currency display
            currency = st.selectbox(
                "Currency Display",
                ["USD", "EUR", "GBP", "BTC"],
                index=["USD", "EUR", "GBP", "BTC"].index(self.app_state.get_setting('currency', 'USD')),
                help="Primary currency for displaying amounts"
            )
            self.app_state.set_setting('currency', currency)
            
            # Timezone
            timezone = st.selectbox(
                "Timezone",
                ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo", "America/Los_Angeles"],
                index=["UTC", "America/New_York", "Europe/London", "Asia/Tokyo", "America/Los_Angeles"].index(
                    self.app_state.get_setting('timezone', 'UTC')
                ),
                help="Timezone for displaying timestamps"
            )
            self.app_state.set_setting('timezone', timezone)
            
            # Max transactions to display
            max_transactions = st.slider(
                "Max Transactions Display",
                min_value=100,
                max_value=5000,
                value=self.app_state.get_setting('max_transactions_display', 1000),
                step=100,
                help="Maximum number of transactions to show in tables"
            )
            self.app_state.set_setting('max_transactions_display', max_transactions)
        
        # Theme preview
        st.markdown("#### Theme Preview")
        with st.container():
            preview_col1, preview_col2, preview_col3 = st.columns(3)
            
            with preview_col1:
                st.markdown("""
                    <div class="metric-card">
                        <div class="metric-label">Sample Metric</div>
                        <div class="metric-value">1,234</div>
                        <div class="metric-delta positive">+5.2%</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with preview_col2:
                st.markdown("""
                    <div class="alert-card medium">
                        <strong>Sample Alert</strong><br>
                        This is how alerts will appear with your current theme settings.
                    </div>
                """, unsafe_allow_html=True)
            
            with preview_col3:
                st.info("This is a sample info message showing your theme colors.")
    
    def _render_notification_settings(self):
        """Render notification preferences"""
        st.markdown("### 🔔 Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Alert Notifications")
            
            # General notifications
            show_notifications = st.checkbox(
                "Enable Notifications",
                value=self.app_state.get_setting('show_notifications', True),
                help="Show system notifications and alerts"
            )
            self.app_state.set_setting('show_notifications', show_notifications)
            
            # Sound alerts
            sound_alerts = st.checkbox(
                "Sound Alerts",
                value=self.app_state.get_setting('enable_sound_alerts', False),
                help="Play sound for critical alerts",
                disabled=not show_notifications
            )
            self.app_state.set_setting('enable_sound_alerts', sound_alerts)
            
            # Alert threshold
            alert_threshold = st.slider(
                "Alert Threshold",
                min_value=50,
                max_value=100,
                value=self.app_state.get_setting('alert_threshold', 80),
                help="Minimum risk score to trigger notifications"
            )
            self.app_state.set_setting('alert_threshold', alert_threshold)
        
        with col2:
            st.markdown("#### Email Notifications")
            
            # Email settings (mock implementation)
            email_enabled = st.checkbox("Enable Email Notifications", value=False)
            
            if email_enabled:
                email_address = st.text_input("Email Address", placeholder="your.email@company.com")
                
                st.markdown("**Email Alert Types:**")
                critical_alerts = st.checkbox("Critical Alerts", value=True)
                daily_summary = st.checkbox("Daily Summary", value=True)
                weekly_report = st.checkbox("Weekly Report", value=False)
                system_alerts = st.checkbox("System Alerts", value=True)
                
                email_frequency = st.selectbox(
                    "Email Frequency",
                    ["Immediate", "Every 15 minutes", "Hourly", "Daily"]
                )
        
        # Notification test
        st.markdown("#### Test Notifications")
        test_col1, test_col2, test_col3 = st.columns(3)
        
        with test_col1:
            if st.button("Test Info Notification"):
                st.info("ℹ️ This is a test information notification")
        
        with test_col2:
            if st.button("Test Warning Notification"):
                st.warning("⚠️ This is a test warning notification")
        
        with test_col3:
            if st.button("Test Error Notification"):
                st.error("🚨 This is a test error notification")
    
    def _render_security_settings(self):
        """Render security and access settings"""
        st.markdown("### 🔒 Security Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Access Control")
            
            # Session settings
            session_timeout = st.selectbox(
                "Session Timeout",
                ["15 minutes", "30 minutes", "1 hour", "4 hours", "8 hours"],
                index=2,
                help="Automatic logout after inactivity"
            )
            
            # Two-factor authentication
            two_factor_enabled = st.checkbox("Two-Factor Authentication", value=True)
            
            if two_factor_enabled:
                st.success("✅ 2FA is enabled for your account")
                if st.button("Configure 2FA"):
                    st.info("2FA configuration would open here")
            else:
                st.warning("⚠️ 2FA is disabled. Enable for better security.")
            
            # API access
            st.markdown("#### API Access")
            api_enabled = st.checkbox("Enable API Access", value=False)
            
            if api_enabled:
                api_key_display = "sk-..." + "*" * 20 + "abc123"
                st.code(api_key_display)
                
                api_col1, api_col2 = st.columns(2)
                with api_col1:
                    if st.button("Generate New Key"):
                        st.success("New API key generated")
                with api_col2:
                    if st.button("Revoke Key"):
                        st.warning("API key revoked")
        
        with col2:
            st.markdown("#### Audit & Logging")
            
            # Audit settings
            audit_enabled = st.checkbox("Enable Audit Logging", value=True)
            
            # Data retention
            audit_retention = st.selectbox(
                "Audit Log Retention",
                ["30 days", "90 days", "1 year", "2 years", "5 years"],
                index=2,
                help="How long to keep audit logs"
            )
            
            # Failed login attempts
            failed_login_threshold = st.number_input(
                "Failed Login Threshold", 
                min_value=3, 
                max_value=10, 
                value=5,
                help="Lock account after this many failed attempts"
            )
            
            # Recent security events
            st.markdown("#### Recent Security Events")
            security_events = [
                {"event": "Successful login", "time": "2 minutes ago", "ip": "192.168.1.100"},
                {"event": "Password changed", "time": "3 days ago", "ip": "192.168.1.100"},
                {"event": "2FA enabled", "time": "1 week ago", "ip": "192.168.1.100"}
            ]
            
            for event in security_events:
                st.markdown(f"• {event['event']} - {event['time']} ({event['ip']})")
    
    def _render_system_settings(self):
        """Render system configuration settings"""
        st.markdown("### ⚙️ System Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Performance")
            
            # Auto-refresh settings
            auto_refresh = st.checkbox(
                "Auto Refresh",
                value=self.app_state.get_setting('auto_refresh', True),
                help="Automatically refresh data"
            )
            self.app_state.set_setting('auto_refresh', auto_refresh)
            
            if auto_refresh:
                refresh_interval = st.slider(
                    "Refresh Interval (seconds)",
                    min_value=10,
                    max_value=300,
                    value=self.app_state.get_setting('refresh_interval', 30),
                    step=10,
                    help="How often to refresh data"
                )
                self.app_state.set_setting('refresh_interval', refresh_interval)
            
            # Real-time features
            enable_realtime = st.checkbox(
                "Enable Real-time Features",
                value=self.app_state.get_setting('enable_real_time', True),
                help="Enable real-time monitoring and updates"
            )
            self.app_state.set_setting('enable_real_time', enable_realtime)
            
            # Debug mode
            debug_mode = st.checkbox(
                "Debug Mode",
                value=self.app_state.get_setting('debug_mode', False),
                help="Enable debug information and verbose logging"
            )
            self.app_state.set_setting('debug_mode', debug_mode)
        
        with col2:
            st.markdown("#### System Information")
            
            # System stats
            st.markdown("**Application Version:** 2.0.0")
            st.markdown("**Build Date:** 2024-12-08")
            st.markdown("**Environment:** Production")
            st.markdown("**Database:** Connected")
            st.markdown("**Cache:** Redis Online")
            
            # System resources
            st.markdown("#### Resource Usage")
            
            # Mock system metrics
            st.metric("Memory Usage", "342 MB", "-12 MB")
            st.metric("CPU Usage", "23.4%", "+2.1%")
            st.metric("Disk Usage", "67.8%", "+0.3%")
            
            # System actions
            st.markdown("#### System Actions")
            
            action_col1, action_col2 = st.columns(2)
            
            with action_col1:
                if st.button("Clear Cache"):
                    self.app_state.clear_cache()
                    st.success("Cache cleared successfully")
            
            with action_col2:
                if st.button("Restart Services"):
                    st.info("Service restart would be initiated")
    
    def _render_data_settings(self):
        """Render data management settings"""
        st.markdown("### 📊 Data Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Data Retention")
            
            # Data retention policies
            transaction_retention = st.selectbox(
                "Transaction Data Retention",
                ["30 days", "90 days", "1 year", "2 years", "5 years", "Indefinite"],
                index=3,
                help="How long to keep transaction data"
            )
            
            alert_retention = st.selectbox(
                "Alert Data Retention",
                ["90 days", "6 months", "1 year", "2 years", "5 years"],
                index=2,
                help="How long to keep alert data"
            )
            
            log_retention = st.selectbox(
                "Log Data Retention",
                ["30 days", "90 days", "6 months", "1 year"],
                index=1,
                help="How long to keep system logs"
            )
            
            # Data archival
            st.markdown("#### Data Archival")
            
            auto_archive = st.checkbox("Enable Auto-Archival", value=True)
            
            if auto_archive:
                archive_threshold = st.selectbox(
                    "Archive After",
                    ["90 days", "6 months", "1 year", "2 years"],
                    index=2
                )
        
        with col2:
            st.markdown("#### Data Export")
            
            # Export options
            export_format = st.selectbox(
                "Default Export Format",
                ["CSV", "JSON", "Excel", "PDF"],
                help="Default format for data exports"
            )
            
            # Data sources
            st.markdown("#### Data Sources")
            
            data_sources = {
                "Internal Database": True,
                "External API": True,
                "Blockchain Data": True,
                "Third-party Feeds": False
            }
            
            for source, enabled in data_sources.items():
                status = "🟢 Connected" if enabled else "🔴 Disabled"
                st.markdown(f"• {source}: {status}")
            
            # Data quality
            st.markdown("#### Data Quality")
            
            st.metric("Data Completeness", "98.7%", "+0.2%")
            st.metric("Data Accuracy", "99.2%", "+0.1%")
            st.metric("Data Freshness", "Real-time", "✅")
            
            # Backup settings
            st.markdown("#### Backup Settings")
            
            backup_enabled = st.checkbox("Enable Automatic Backups", value=True)
            
            if backup_enabled:
                backup_frequency = st.selectbox(
                    "Backup Frequency",
                    ["Daily", "Weekly", "Monthly"],
                    index=0
                )
                
                st.markdown("**Last Backup:** 2 hours ago ✅")
        
        # Settings management
        st.markdown("---")
        st.markdown("### 🔧 Settings Management")
        
        settings_col1, settings_col2, settings_col3 = st.columns(3)
        
        with settings_col1:
            if st.button("💾 Export Settings"):
                settings_json = self.app_state.export_settings()
                st.download_button(
                    label="📥 Download Settings",
                    data=settings_json,
                    file_name=f"synapse_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with settings_col2:
            uploaded_file = st.file_uploader("📤 Import Settings", type=['json'])
            if uploaded_file is not None:
                try:
                    settings_data = json.load(uploaded_file)
                    if st.button("Apply Imported Settings"):
                        success = self.app_state.import_settings(json.dumps(settings_data))
                        if success:
                            st.success("Settings imported successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to import settings")
                except Exception as e:
                    st.error(f"Invalid settings file: {str(e)}")
        
        with settings_col3:
            if st.button("🔄 Reset to Defaults"):
                if st.button("⚠️ Confirm Reset", type="secondary"):
                    self.app_state.reset_settings()
                    st.success("Settings reset to defaults!")
                    st.rerun()
                else:
                    st.warning("Click 'Confirm Reset' to proceed")