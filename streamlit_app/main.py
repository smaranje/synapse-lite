"""
Synapse-Lite Fraud Detection System
Re-engineered Streamlit Application

A modern, enterprise-grade Bitcoin fraud detection dashboard with real-time monitoring,
AI-powered analytics, and professional visualization capabilities.

Author: AI Assistant
Version: 2.0.0
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Configure page settings first
st.set_page_config(
    page_title="Synapse-Lite | Bitcoin Fraud Detection",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': 'https://github.com/your-repo/issues',
        'About': '# Synapse-Lite\nEnterprise-grade Bitcoin fraud detection system'
    }
)

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Core imports
from core.app_state import AppState
from core.theme_manager import ThemeManager
from core.navigation import NavigationManager
from ui.components.sidebar import SidebarManager
from ui.components.header import HeaderManager
from ui.components.footer import FooterManager

# Page imports
from pages.overview import OverviewPage
from pages.realtime import RealtimePage
from pages.transactions import TransactionsPage
from pages.alerts import AlertsPage
from pages.analytics import AnalyticsPage
from pages.investigations import InvestigationsPage
from pages.reports import ReportsPage
from pages.settings import SettingsPage

class SynapseLiteApp:
    """Main application class for Synapse-Lite fraud detection system"""
    
    def __init__(self):
        self.app_state = AppState()
        self.theme_manager = ThemeManager()
        self.navigation = NavigationManager()
        self.sidebar = SidebarManager(self.app_state)
        self.header = HeaderManager(self.app_state)
        self.footer = FooterManager()
        
        # Initialize pages
        self.pages = {
            "overview": OverviewPage(self.app_state),
            "realtime": RealtimePage(self.app_state),
            "transactions": TransactionsPage(self.app_state),
            "alerts": AlertsPage(self.app_state),
            "analytics": AnalyticsPage(self.app_state),
            "investigations": InvestigationsPage(self.app_state),
            "reports": ReportsPage(self.app_state),
            "settings": SettingsPage(self.app_state)
        }
    
    def initialize(self):
        """Initialize the application"""
        # Apply theme and styling
        self.theme_manager.apply_theme()
        
        # Initialize app state
        self.app_state.initialize()
        
        # Check for real-time updates
        if self.app_state.get_setting('auto_refresh', True):
            self.app_state.refresh_data()
    
    def render(self):
        """Render the main application"""
        try:
            # Initialize app
            self.initialize()
            
            # Render header
            self.header.render()
            
            # Create main layout
            sidebar_col, main_col = st.columns([1, 4])
            
            with sidebar_col:
                # Render sidebar and get current page
                current_page = self.sidebar.render()
            
            with main_col:
                # Render the selected page
                if current_page in self.pages:
                    self.pages[current_page].render()
                else:
                    # Default to overview
                    self.pages["overview"].render()
            
            # Render footer
            self.footer.render()
            
        except Exception as e:
            st.error(f"Application Error: {str(e)}")
            if self.app_state.get_setting('debug_mode', False):
                st.exception(e)

def main():
    """Main application entry point"""
    app = SynapseLiteApp()
    app.render()

if __name__ == "__main__":
    main()