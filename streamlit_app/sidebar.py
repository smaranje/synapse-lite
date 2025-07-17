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
        # Logo at the top, centered using st.image
        st.image("logo.png", width=64)
        st.markdown(
            '<div style="text-align:center; margin-bottom:2rem; margin-top:0.5rem;">
                <span style="font-weight:700;font-size:1.25rem;color:#222;letter-spacing:-0.01em;">Synapse-Lite</span>
            </div>',
            unsafe_allow_html=True
        )
        # Navigation radio with more spacing and no emojis
        nav_labels = list(PAGES.keys())
        selected_page = st.radio(
            "",
            nav_labels,
            label_visibility="collapsed",
            index=0,
            key="main_nav"
        )
        # Sidebar CSS for white background, spacing, and improved typography
        st.markdown(
            '''<style>
            [data-testid="stSidebar"] {
                background: #fff !important;
                border-right: 1px solid #f0f3f7;
                min-width: 220px;
                max-width: 260px;
                padding-top: 0 !important;
            }
            [data-testid="stSidebar"] .stRadio > div { gap: 1rem; }
            [data-testid="stSidebar"] label {
                font-size: 1.12rem;
                font-weight: 500;
                color: #222 !important;
                padding: 1rem 1.25rem;
                border-radius: 8px;
                margin-bottom: 0.75rem;
                transition: background 0.15s;
                letter-spacing: 0.01em;
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