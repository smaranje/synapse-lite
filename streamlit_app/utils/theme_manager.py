"""
Theme Manager for Synapse-Lite Dashboard
Handles dark mode preferences and theme switching
"""

import streamlit as st

def init_theme():
    """Initialize theme in session state"""
    if 'dark_mode' not in st.session_state:
        # Default to system preference
        st.session_state.dark_mode = None  # None means follow system
    
def get_theme_override_css():
    """Get CSS to override theme based on user preference"""
    if st.session_state.dark_mode is None:
        return ""  # Use system preference
    
    if st.session_state.dark_mode:
        # Force dark mode
        return """
        <style>
            :root {
                --bg-primary: #0a0a0a !important;
                --bg-secondary: #1a1a1a !important;
                --bg-card: #1f1f1f !important;
                --text-primary: #ffffff !important;
                --text-secondary: #a1a1aa !important;
                --text-tertiary: #71717a !important;
                --border-color: #27272a !important;
                --border-light: #2a2a2a !important;
                --primary-color: #3b82f6 !important;
                --primary-hover: #2563eb !important;
                --success-color: #10b981 !important;
                --success-hover: #059669 !important;
                --danger-color: #ef4444 !important;
                --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
                --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
                --shadow-primary: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
                --shadow-primary-hover: 0 8px 24px rgba(59, 130, 246, 0.4) !important;
            }
            
            .stApp {
                background-color: var(--bg-primary) !important;
            }
            
            .js-plotly-plot .plotly {
                background: var(--bg-card) !important;
            }
            
            .js-plotly-plot .plotly .bg {
                fill: var(--bg-card) !important;
            }
            
            .js-plotly-plot .plotly text {
                fill: var(--text-secondary) !important;
            }
            
            p, span, div {
                color: var(--text-primary) !important;
            }
            
            input, textarea, select {
                background: var(--bg-card) !important;
                color: var(--text-primary) !important;
                border-color: var(--border-color) !important;
            }
            
            [data-baseweb="select"] {
                background: var(--bg-card) !important;
            }
            
            [data-baseweb="select"] > div {
                background: var(--bg-card) !important;
                color: var(--text-primary) !important;
            }
        </style>
        """
    else:
        # Force light mode
        return """
        <style>
            :root {
                --bg-primary: #ffffff !important;
                --bg-secondary: #fafbfc !important;
                --bg-card: #ffffff !important;
                --text-primary: #050f19 !important;
                --text-secondary: #5e6278 !important;
                --text-tertiary: #6b7280 !important;
                --border-color: #e5e7eb !important;
                --border-light: #f0f2f5 !important;
                --primary-color: #0052FF !important;
                --primary-hover: #0041d0 !important;
                --success-color: #00D395 !important;
                --success-hover: #00B880 !important;
                --danger-color: #FF5252 !important;
                --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
                --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
                --shadow-primary: 0 4px 12px rgba(0, 82, 255, 0.15) !important;
                --shadow-primary-hover: 0 8px 24px rgba(0, 82, 255, 0.25) !important;
            }
            
            .stApp {
                background-color: var(--bg-primary) !important;
            }
            
            .js-plotly-plot .plotly {
                background: var(--bg-card) !important;
            }
            
            .js-plotly-plot .plotly .bg {
                fill: var(--bg-card) !important;
            }
        </style>
        """

def render_theme_toggle():
    """Render theme toggle in sidebar"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Theme Settings")
        
        theme_options = {
            "System Default": None,
            "Light Mode": False,
            "Dark Mode": True
        }
        
        # Find current selection
        current_theme = "System Default"
        for name, value in theme_options.items():
            if st.session_state.dark_mode == value:
                current_theme = name
                break
        
        selected_theme = st.selectbox(
            "Choose theme:",
            options=list(theme_options.keys()),
            index=list(theme_options.keys()).index(current_theme),
            key="theme_selector"
        )
        
        new_value = theme_options[selected_theme]
        if new_value != st.session_state.dark_mode:
            st.session_state.dark_mode = new_value
            st.rerun()