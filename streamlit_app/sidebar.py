# Sidebar component for Streamlit app

import streamlit as st
import random
import sys
import os

# Add the current directory to the Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import PAGES
from utils import create_status_indicator

def render_sidebar():
    """Render the enterprise-style sidebar navigation and return selected page"""
    page_icons = {
        "Dashboard": "🏠",
        "Analytics": "📊",
        "Transactions": "💸",
        "Alerts": "⚠️",
        "Settings": "⚙️"
    }
    with st.sidebar:
        st.markdown(
            '''<div style="display:flex;align-items:center;gap:0.5rem;padding:1.5rem 0 1.5rem 0;">
                <span style="font-size:2rem;line-height:1;">🔷</span>
                <span style="font-weight:700;font-size:1.25rem;color:#222;letter-spacing:-0.01em;">Synapse-Lite</span>
            </div>''',
            unsafe_allow_html=True
        )
        selected_page = st.radio(
            "",
            list(PAGES.keys()),
            format_func=lambda x: f"{page_icons.get(x, '')}  {PAGES[x]}",
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
        # System status as small footer
        st.markdown('<div style="height:2rem;"></div>', unsafe_allow_html=True)
        st.markdown(
            '''<div style="position:absolute;bottom:2rem;left:1.5rem;font-size:0.95rem;color:#888;">
                <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#22c55e;margin-right:6px;"></span> Neo4j
                <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#0a7cff;margin:0 6px 0 18px;"></span> Kafka
                <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:#f59e42;margin:0 6px 0 18px;"></span> AI
            </div>''',
            unsafe_allow_html=True
        )
    return selected_page