"""
Header Manager for Synapse-Lite
Modern application header with breadcrumbs and real-time status
"""

import streamlit as st
from datetime import datetime
from core.navigation import NavigationManager

class HeaderManager:
    """Manages the application header"""
    
    def __init__(self, app_state):
        self.app_state = app_state
        self.navigation = NavigationManager()
    
    def render(self):
        """Render the application header"""
        self._render_main_header()
        self._render_breadcrumbs()
    
    def _render_main_header(self):
        """Render the main header with status and actions"""
        col1, col2, col3 = st.columns([2, 3, 2])
        
        with col1:
            current_page = self.navigation.get_current_page_info()
            st.markdown(f"""
                <div class="app-header">
                    <h1 class="app-title">
                        {current_page.get('icon', '🔷')} {current_page.get('title', 'Synapse-Lite')}
                    </h1>
                    <p class="app-subtitle">{current_page.get('description', 'Bitcoin Fraud Detection System')}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            self._render_realtime_indicators()
        
        with col3:
            self._render_header_actions()
    
    def _render_realtime_indicators(self):
        """Render real-time system indicators"""
        from data.data_service import DataService
        data_service = DataService()
        realtime_data = data_service.get_realtime_data()
        
        # Create indicator row
        indicator_col1, indicator_col2, indicator_col3 = st.columns(3)
        
        with indicator_col1:
            tps = realtime_data.get('transactions_per_second', 0)
            st.metric(
                "TPS", 
                f"{tps}",
                delta=f"{realtime_data.get('success_rate', 0):.1f}% success"
            )
        
        with indicator_col2:
            load = realtime_data.get('current_load', 0)
            load_color = "🟢" if load < 70 else "🟡" if load < 90 else "🔴"
            st.metric(
                "System Load",
                f"{load_color} {load}%",
                delta=f"{realtime_data.get('active_connections', 0)} conn"
            )
        
        with indicator_col3:
            risk_level = realtime_data.get('current_risk_level', 'low')
            risk_icons = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
            st.metric(
                "Risk Level",
                f"{risk_icons.get(risk_level, '⚪')} {risk_level.title()}",
                delta=f"{realtime_data.get('ai_model_accuracy', 0):.1f}% accuracy"
            )
    
    def _render_header_actions(self):
        """Render header action buttons"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Theme toggle
            current_theme = self.app_state.get_setting('theme', 'dark')
            theme_icon = "🌙" if current_theme == 'dark' else "☀️"
            if st.button(theme_icon, help="Toggle theme"):
                new_theme = 'light' if current_theme == 'dark' else 'dark'
                self.app_state.set_setting('theme', new_theme)
                st.rerun()
        
        with col2:
            # Auto-refresh toggle
            auto_refresh = self.app_state.get_setting('auto_refresh', True)
            refresh_icon = "🔄" if auto_refresh else "⏸️"
            if st.button(refresh_icon, help="Toggle auto-refresh"):
                self.app_state.set_setting('auto_refresh', not auto_refresh)
                st.rerun()
        
        with col3:
            # Notifications
            alerts_count = len([a for a in self.app_state.get_alerts_data() if a.get('status') == 'active'])
            notification_text = f"🔔 {alerts_count}" if alerts_count > 0 else "🔕"
            if st.button(notification_text, help="View notifications"):
                self.navigation.navigate_to('alerts')
                st.rerun()
    
    def _render_breadcrumbs(self):
        """Render breadcrumb navigation"""
        breadcrumbs = self.navigation.get_breadcrumbs()
        
        if len(breadcrumbs) > 1:
            breadcrumb_html = ""
            for i, crumb in enumerate(breadcrumbs):
                if i > 0:
                    breadcrumb_html += " <span style='color: var(--secondary-text);'>/</span> "
                
                if crumb.get('key') and crumb['key'] != self.navigation.get_current_page():
                    breadcrumb_html += f"<a href='#' style='color: var(--accent-blue); text-decoration: none;'>{crumb['title']}</a>"
                else:
                    breadcrumb_html += f"<span style='color: var(--primary-text);'>{crumb['title']}</span>"
            
            st.markdown(f"""
                <div style="margin: 1rem 0; padding: 0.5rem 0; border-bottom: 1px solid var(--border-color);">
                    <div style="font-size: 0.875rem; color: var(--secondary-text);">
                        {breadcrumb_html}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    def _render_status_banner(self):
        """Render status banner for important system notifications"""
        # Check for critical alerts or system issues
        alerts = self.app_state.get_alerts_data()
        critical_alerts = [a for a in alerts if a.get('severity') == 'critical' and a.get('status') == 'active']
        
        if critical_alerts:
            st.error(f"🚨 {len(critical_alerts)} critical alert(s) require immediate attention!")
        
        # Check system health
        metrics = self.app_state.get_system_metrics()
        uptime = metrics.get('uptime_hours', 0)
        
        if uptime < 1:
            st.warning("⚠️ System recently restarted. Data may be incomplete.")
        
        # Check data freshness
        if self.app_state.should_refresh_data():
            st.info("💡 Data refresh recommended. Click refresh or enable auto-refresh.")
    
    def render_page_header(self, title: str, description: str = "", actions: list = None):
        """Render a page-specific header"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"""
                <div style="margin-bottom: 2rem;">
                    <h1 style="color: var(--primary-text); margin: 0 0 0.5rem 0; font-size: 2rem;">
                        {title}
                    </h1>
                    {f'<p style="color: var(--secondary-text); margin: 0; font-size: 1rem;">{description}</p>' if description else ''}
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if actions:
                for action in actions:
                    if st.button(action.get('label', 'Action'), key=action.get('key', 'action')):
                        if action.get('callback'):
                            action['callback']()
    
    def render_data_timestamp(self):
        """Render when data was last updated"""
        last_updated = self.app_state.get_data_last_updated()
        if last_updated:
            time_ago = datetime.now() - last_updated
            if time_ago.total_seconds() < 60:
                time_str = "Just now"
            elif time_ago.total_seconds() < 3600:
                time_str = f"{int(time_ago.total_seconds() / 60)} minutes ago"
            else:
                time_str = f"{int(time_ago.total_seconds() / 3600)} hours ago"
            
            st.markdown(f"""
                <div style="text-align: right; font-size: 0.8rem; color: var(--secondary-text); margin-bottom: 1rem;">
                    Last updated: {time_str}
                </div>
            """, unsafe_allow_html=True)