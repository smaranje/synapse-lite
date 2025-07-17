"""
Theme Manager for Synapse-Lite
Modern, responsive UI styling with dark/light theme support
"""

import streamlit as st
from typing import Dict, Any

class ThemeManager:
    """Manages application themes and styling"""
    
    def __init__(self):
        self.themes = {
            'dark': self._get_dark_theme(),
            'light': self._get_light_theme()
        }
    
    def _get_dark_theme(self) -> Dict[str, Any]:
        """Dark theme configuration"""
        return {
            'primary_bg': '#0f1419',
            'secondary_bg': '#1a1f2e',
            'tertiary_bg': '#242a3a',
            'primary_text': '#ffffff',
            'secondary_text': '#b0b8c9',
            'accent_blue': '#0052ff',
            'accent_green': '#00d924', 
            'accent_red': '#ff4757',
            'accent_orange': '#ff9500',
            'border_color': '#2d3748',
            'hover_bg': '#2a3441',
            'success': '#48bb78',
            'warning': '#ed8936',
            'error': '#f56565',
            'info': '#4299e1'
        }
    
    def _get_light_theme(self) -> Dict[str, Any]:
        """Light theme configuration"""
        return {
            'primary_bg': '#ffffff',
            'secondary_bg': '#f7fafc',
            'tertiary_bg': '#edf2f7',
            'primary_text': '#1a202c',
            'secondary_text': '#4a5568',
            'accent_blue': '#0052ff',
            'accent_green': '#00d924',
            'accent_red': '#ff4757',
            'accent_orange': '#ff9500',
            'border_color': '#e2e8f0',
            'hover_bg': '#f1f5f9',
            'success': '#38a169',
            'warning': '#d69e2e',
            'error': '#e53e3e',
            'info': '#3182ce'
        }
    
    def apply_theme(self):
        """Apply the selected theme to the application"""
        # Get theme preference
        theme_name = st.session_state.get('user_settings', {}).get('theme', 'dark')
        theme = self.themes.get(theme_name, self.themes['dark'])
        
        # Apply custom CSS
        css = self._generate_css(theme)
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    def _generate_css(self, theme: Dict[str, Any]) -> str:
        """Generate CSS based on theme configuration"""
        return f"""
        /* Import modern fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500&display=swap');
        
        /* CSS Variables for theme */
        :root {{
            --primary-bg: {theme['primary_bg']};
            --secondary-bg: {theme['secondary_bg']};
            --tertiary-bg: {theme['tertiary_bg']};
            --primary-text: {theme['primary_text']};
            --secondary-text: {theme['secondary_text']};
            --accent-blue: {theme['accent_blue']};
            --accent-green: {theme['accent_green']};
            --accent-red: {theme['accent_red']};
            --accent-orange: {theme['accent_orange']};
            --border-color: {theme['border_color']};
            --hover-bg: {theme['hover_bg']};
            --success: {theme['success']};
            --warning: {theme['warning']};
            --error: {theme['error']};
            --info: {theme['info']};
        }}
        
        /* Base Application Styling */
        .main, .stApp, [data-testid="stAppViewContainer"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            background-color: var(--primary-bg) !important;
            color: var(--primary-text) !important;
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{display: none;}}
        
        /* Sidebar Styling */
        .css-1d391kg, .css-1outpf7 {{
            background-color: var(--secondary-bg) !important;
            border-right: 1px solid var(--border-color) !important;
        }}
        
        /* Custom Card Styling */
        .metric-card {{
            background: var(--tertiary-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            margin: 0.5rem 0 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
            transition: all 0.3s ease !important;
            color: var(--primary-text) !important;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            background: var(--hover-bg) !important;
        }}
        
        .metric-value {{
            font-size: 2rem !important;
            font-weight: 700 !important;
            color: var(--primary-text) !important;
            margin: 0.5rem 0 !important;
        }}
        
        .metric-label {{
            font-size: 0.875rem !important;
            color: var(--secondary-text) !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
            font-weight: 500 !important;
        }}
        
        .metric-delta {{
            font-size: 0.875rem !important;
            font-weight: 500 !important;
            margin-top: 0.25rem !important;
        }}
        
        .metric-delta.positive {{
            color: var(--success) !important;
        }}
        
        .metric-delta.negative {{
            color: var(--error) !important;
        }}
        
        /* Alert Cards */
        .alert-card {{
            background: var(--tertiary-bg) !important;
            border-left: 4px solid var(--accent-red) !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }}
        
        .alert-card.high {{
            border-left-color: var(--error) !important;
        }}
        
        .alert-card.medium {{
            border-left-color: var(--warning) !important;
        }}
        
        .alert-card.low {{
            border-left-color: var(--info) !important;
        }}
        
        /* Status Badges */
        .status-badge {{
            padding: 0.25rem 0.75rem !important;
            border-radius: 20px !important;
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.05em !important;
        }}
        
        .status-active {{
            background: var(--success) !important;
            color: white !important;
        }}
        
        .status-pending {{
            background: var(--warning) !important;
            color: white !important;
        }}
        
        .status-resolved {{
            background: var(--secondary-text) !important;
            color: white !important;
        }}
        
        /* Button Styling */
        .stButton > button {{
            background: var(--accent-blue) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton > button:hover {{
            background: #0046e6 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 8px rgba(0,82,255,0.3) !important;
        }}
        
        /* Secondary Button */
        .btn-secondary {{
            background: var(--secondary-bg) !important;
            color: var(--primary-text) !important;
            border: 1px solid var(--border-color) !important;
        }}
        
        .btn-secondary:hover {{
            background: var(--hover-bg) !important;
        }}
        
        /* Header Styling */
        .app-header {{
            background: var(--secondary-bg) !important;
            border-bottom: 1px solid var(--border-color) !important;
            padding: 1rem 2rem !important;
            margin-bottom: 2rem !important;
        }}
        
        .app-title {{
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            color: var(--primary-text) !important;
            margin: 0 !important;
        }}
        
        .app-subtitle {{
            font-size: 0.875rem !important;
            color: var(--secondary-text) !important;
            margin: 0 !important;
        }}
        
        /* Navigation Styling */
        .nav-item {{
            display: flex !important;
            align-items: center !important;
            padding: 0.75rem 1rem !important;
            border-radius: 8px !important;
            margin: 0.25rem 0 !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            color: var(--secondary-text) !important;
            text-decoration: none !important;
        }}
        
        .nav-item:hover {{
            background: var(--hover-bg) !important;
            color: var(--primary-text) !important;
        }}
        
        .nav-item.active {{
            background: var(--accent-blue) !important;
            color: white !important;
        }}
        
        .nav-icon {{
            margin-right: 0.75rem !important;
            font-size: 1.125rem !important;
        }}
        
        /* Table Styling */
        .stDataFrame {{
            background: var(--tertiary-bg) !important;
            border-radius: 8px !important;
            border: 1px solid var(--border-color) !important;
        }}
        
        /* Chart Styling */
        .plot-container {{
            background: var(--tertiary-bg) !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            border: 1px solid var(--border-color) !important;
        }}
        
        /* Input Styling */
        .stTextInput > div > div > input {{
            background: var(--tertiary-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            color: var(--primary-text) !important;
        }}
        
        .stSelectbox > div > div > div {{
            background: var(--tertiary-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            color: var(--primary-text) !important;
        }}
        
        /* Progress Bar */
        .stProgress > div > div > div {{
            background: var(--accent-blue) !important;
        }}
        
        /* Expandable Sections */
        .streamlit-expanderHeader {{
            background: var(--tertiary-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            color: var(--primary-text) !important;
        }}
        
        /* Code Blocks */
        .stCode {{
            background: var(--tertiary-bg) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            font-family: 'JetBrains Mono', 'Monaco', 'Menlo', monospace !important;
        }}
        
        /* Success/Error Messages */
        .stSuccess {{
            background: rgba(72, 187, 120, 0.1) !important;
            border: 1px solid var(--success) !important;
            color: var(--success) !important;
        }}
        
        .stError {{
            background: rgba(245, 101, 101, 0.1) !important;
            border: 1px solid var(--error) !important;
            color: var(--error) !important;
        }}
        
        .stWarning {{
            background: rgba(237, 137, 54, 0.1) !important;
            border: 1px solid var(--warning) !important;
            color: var(--warning) !important;
        }}
        
        .stInfo {{
            background: rgba(66, 153, 225, 0.1) !important;
            border: 1px solid var(--info) !important;
            color: var(--info) !important;
        }}
        
        /* Footer */
        .app-footer {{
            border-top: 1px solid var(--border-color) !important;
            padding: 2rem !important;
            margin-top: 3rem !important;
            text-align: center !important;
            color: var(--secondary-text) !important;
            font-size: 0.875rem !important;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .metric-card {{
                padding: 1rem !important;
            }}
            
            .metric-value {{
                font-size: 1.5rem !important;
            }}
            
            .app-header {{
                padding: 1rem !important;
            }}
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .animate-in {{
            animation: fadeIn 0.5s ease-out !important;
        }}
        
        /* Loading States */
        .loading-skeleton {{
            background: linear-gradient(
                90deg,
                var(--tertiary-bg) 25%,
                var(--hover-bg) 50%,
                var(--tertiary-bg) 75%
            ) !important;
            background-size: 200% 100% !important;
            animation: loading 1.5s infinite !important;
        }}
        
        @keyframes loading {{
            0% {{ background-position: 200% 0; }}
            100% {{ background-position: -200% 0; }}
        }}
        """
    
    def get_current_theme(self) -> str:
        """Get the current theme name"""
        return st.session_state.get('user_settings', {}).get('theme', 'dark')
    
    def set_theme(self, theme_name: str):
        """Set the current theme"""
        if theme_name in self.themes:
            if 'user_settings' not in st.session_state:
                st.session_state.user_settings = {}
            st.session_state.user_settings['theme'] = theme_name
            self.apply_theme()
    
    def get_theme_colors(self, theme_name: str = None) -> Dict[str, Any]:
        """Get theme colors for use in charts and components"""
        if not theme_name:
            theme_name = self.get_current_theme()
        return self.themes.get(theme_name, self.themes['dark'])