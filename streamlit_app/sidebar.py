# Sidebar component for Streamlit app - Coinbase Business Style

import streamlit as st
import random
import sys
import os

# Add the current directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import PAGES
from utils import create_status_indicator

def render_sidebar():
    """Render the Coinbase Business-style sidebar navigation and return selected page"""
    with st.sidebar:
        # Coinbase Business branding
        st.markdown(
            '''<div style="padding: 2rem 1rem 1.5rem 1rem; border-bottom: 1px solid var(--cb-gray-200);">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div style="width: 32px; height: 32px; background: var(--cb-blue); border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 1rem;">S</div>
                    <div>
                        <div style="font-weight: 600; font-size: 1.1rem; color: var(--cb-gray-900); line-height: 1.2;">Synapse-Lite</div>
                        <div style="font-size: 0.8rem; color: var(--cb-gray-500);">Business</div>
                    </div>
                </div>
            </div>''',
            unsafe_allow_html=True
        )
        
        # Navigation with Coinbase-style icons
        st.markdown('<div style="padding: 1rem 0;">', unsafe_allow_html=True)
        
        # Custom navigation styling
        st.markdown(
            '''<style>
            /* Sidebar styling */
            [data-testid="stSidebar"] {
                background: white !important;
                border-right: 1px solid var(--cb-gray-200) !important;
                min-width: 240px !important;
                max-width: 240px !important;
                padding-top: 0 !important;
            }
            
            /* Radio button styling */
            [data-testid="stSidebar"] .stRadio > div { 
                gap: 0.25rem; 
                padding: 0 1rem;
            }
            
            [data-testid="stSidebar"] .stRadio > div > label {
                display: flex !important;
                align-items: center !important;
                gap: 0.75rem !important;
                padding: 0.75rem 1rem !important;
                margin: 0.125rem 0 !important;
                border-radius: 8px !important;
                background: transparent !important;
                color: var(--cb-gray-700) !important;
                font-weight: 500 !important;
                font-size: 0.875rem !important;
                cursor: pointer !important;
                transition: all 0.2s ease !important;
                border: none !important;
                width: 100% !important;
            }
            
            [data-testid="stSidebar"] .stRadio > div > label:hover {
                background: var(--cb-gray-50) !important;
                color: var(--cb-gray-900) !important;
            }
            
            [data-testid="stSidebar"] .stRadio > div > label[data-baseweb="radio"] > div:first-child {
                display: none !important;
            }
            
            [data-testid="stSidebar"] .stRadio > div > label[aria-checked="true"] {
                background: var(--cb-blue) !important;
                color: white !important;
                font-weight: 600 !important;
            }
            
            [data-testid="stSidebar"] .stRadio > div > label > div {
                font-size: 0.875rem !important;
            }
            </style>''',
            unsafe_allow_html=True
        )
        
        # Navigation items with icons
        page_options = []
        page_icons = {
            "Dashboard": "🏠",
            "Transactions": "💳", 
            "Analytics": "📊",
            "Alerts": "🔔",
            "Settings": "⚙️"
        }
        
        for page_key in PAGES.keys():
            icon = page_icons.get(page_key, "📄")
            page_options.append(f"{icon} {PAGES[page_key]}")
        
        selected_page_display = st.radio(
            "",
            page_options,
            label_visibility="collapsed",
            index=0,
            key="main_nav"
        )
        
        # Extract the actual page key from the display
        selected_page = None
        for i, (page_key, page_name) in enumerate(PAGES.items()):
            if page_options[i] == selected_page_display:
                selected_page = page_key
                break
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Account info section
        st.markdown(
            '''<div style="position: absolute; bottom: 2rem; left: 1rem; right: 1rem; padding: 1rem; background: var(--cb-gray-50); border-radius: 8px; border: 1px solid var(--cb-gray-200);">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div style="width: 32px; height: 32px; background: var(--cb-blue); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 0.875rem;">LT</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 0.875rem; color: var(--cb-gray-900);">Lightray</div>
                        <div style="font-size: 0.75rem; color: var(--cb-gray-500);">lightray@example.com</div>
                    </div>
                </div>
            </div>''',
            unsafe_allow_html=True
        )
        
        return selected_page