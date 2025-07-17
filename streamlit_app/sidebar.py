# Sidebar component for Streamlit app

import streamlit as st
import sys
import os

# Add the current directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import PAGES

def render_sidebar():
    """Render the enterprise-style sidebar navigation and return selected page"""
    with st.sidebar:
        st.image("logo.png", width=64)
        st.markdown(
            '<div style="text-align:center; margin-bottom:1.5rem; margin-top:0.5rem;">'
            '<span style="font-weight:700;font-size:1.25rem;color:#222;letter-spacing:-0.01em;">Synapse-Lite</span>'
            '</div>',
            unsafe_allow_html=True
        )
        selected_page = st.radio(
            "",
            list(PAGES.keys()),
            format_func=lambda x: f"{PAGES[x]}  {x}",
            label_visibility="collapsed",
            index=0,
            key="main_nav"
        )
        st.markdown(
            '''<style>
            [data-testid="stSidebar"] {
                background: #fff !important;
                border-right: 1px solid #f0f3f7;
                min-width: 220px;
                max-width: 260px;
                padding-top: 0 !important;
            }
            [data-testid="stSidebar"] .stRadio > div { gap: 0.5rem; }
            [data-testid="stSidebar"] label {
                font-size: 1.08rem;
                font-weight: 500;
                color: #222 !important;
                padding: 0.5rem 0.75rem;
                border-radius: 8px;
                margin-bottom: 0.25rem;
                transition: background 0.15s;
            }
            [data-testid="stSidebar"] label[data-selected="true"] {
                background: #eaf1ff !important;
                color: #0052ff !important;
                font-weight: 700;
            }
            [data-testid="stSidebar"] .stRadio > div > div { width: 100%; }
            </style>''',
            unsafe_allow_html=True
        )
    return selected_page