"""
Sidebar Manager for Synapse-Lite
Modern navigation sidebar with system status and quick actions
"""

import streamlit as st
from datetime import datetime
from core.navigation import NavigationManager

class SidebarManager:
    """Manages the application sidebar"""
    
    def __init__(self, app_state):
        self.app_state = app_state
        self.navigation = NavigationManager()
    
    def render(self) -> str:
        """Render the sidebar and return selected page"""
        with st.sidebar:
            self._render_logo()
            self._render_navigation()
            self._render_system_status()
            self._render_quick_actions()
            return self.navigation.get_current_page()
    
    def _render_logo(self):
        """Render application logo and title"""
        st.markdown("""
            <div style="text-align: center; padding: 1rem 0 2rem 0;">
                <h1 style="color: var(--accent-blue); font-size: 1.5rem; margin: 0;">
                    🔷 Synapse-Lite
                </h1>
                <p style="color: var(--secondary-text); font-size: 0.8rem; margin: 0.5rem 0 0 0;">
                    Bitcoin Fraud Detection
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    def _render_navigation(self):
        """Render navigation menu"""
        st.markdown("### Navigation")
        
        menu = self.navigation.get_navigation_menu()
        current_page = self.navigation.get_current_page()
        
        # Group pages by category
        category_order = ['main', 'analysis', 'investigation', 'admin']
        category_titles = {
            'main': '🏠 Main',
            'analysis': '📊 Analysis', 
            'investigation': '🔍 Investigation',
            'admin': '⚙️ Administration'
        }
        
        for category in category_order:
            if category in menu:
                if category != 'main':  # Don't show header for main category
                    st.markdown(f"**{category_titles[category]}**")
                
                for page in menu[category]:
                    is_current = self.navigation.is_current_page(page['key'])
                    
                    # Create button style based on selection
                    button_style = "primary" if is_current else "secondary"
                    
                    if st.button(
                        f"{page['icon']} {page['title']}", 
                        key=f"nav_{page['key']}",
                        use_container_width=True,
                        type=button_style
                    ):
                        self.navigation.navigate_to(page['key'])
                        st.rerun()
                
                if category != 'admin':  # Don't add spacing after last category
                    st.markdown("---")
    
    def _render_system_status(self):
        """Render system status widget"""
        st.markdown("### System Status")
        
        # Get system metrics
        metrics = self.app_state.get_system_metrics()
        
        # System health indicator
        uptime_hours = metrics.get('uptime_hours', 0)
        if uptime_hours > 24:
            status_color = "var(--success)"
            status_text = "🟢 Online"
        elif uptime_hours > 1:
            status_color = "var(--warning)"
            status_text = "🟡 Monitoring"
        else:
            status_color = "var(--error)"
            status_text = "🔴 Starting"
        
        st.markdown(f"""
            <div class="metric-card">
                <div style="color: {status_color}; font-weight: 600; margin-bottom: 0.5rem;">
                    {status_text}
                </div>
                <div style="font-size: 0.8rem; color: var(--secondary-text);">
                    Uptime: {uptime_hours:.1f}h
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        stats = self.app_state.get_summary_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Transactions",
                f"{stats.get('total_transactions_today', 0):,}",
                delta=f"+{stats.get('processing_rate', 0)}/s"
            )
        
        with col2:
            st.metric(
                "Active Alerts", 
                stats.get('active_alerts', 0),
                delta=f"{stats.get('avg_risk_score', 0):.1f} avg risk"
            )
    
    def _render_quick_actions(self):
        """Render quick action buttons"""
        st.markdown("### Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            self.app_state.refresh_data()
            st.success("Data refreshed!")
            st.rerun()
        
        if st.button("🚨 New Alert", use_container_width=True):
            self._create_manual_alert()
        
        if st.button("📊 Export Data", use_container_width=True):
            self._show_export_options()
    
    def _create_manual_alert(self):
        """Create a manual alert"""
        # This would typically open a modal or navigate to alert creation
        new_alert = {
            'type': 'Manual Review',
            'severity': 'medium',
            'description': 'Manual alert created by user',
            'status': 'active'
        }
        self.app_state.add_alert(new_alert)
        st.success("Manual alert created!")
    
    def _show_export_options(self):
        """Show export options"""
        st.info("Export functionality - would show export dialog")
    
    def _render_last_updated(self):
        """Render last updated timestamp"""
        last_updated = self.app_state.get_data_last_updated()
        if last_updated:
            time_str = last_updated.strftime("%H:%M:%S")
            st.markdown(f"""
                <div style="text-align: center; font-size: 0.7rem; color: var(--secondary-text); margin-top: 1rem;">
                    Last updated: {time_str}
                </div>
            """, unsafe_allow_html=True)