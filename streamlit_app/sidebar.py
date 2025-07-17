"""Sidebar component for the fraud detection system."""

import streamlit as st
import random
from .config import PAGES
from .utils import create_status_indicator

def render_sidebar():
    """Render the enhanced sidebar with navigation and quick stats."""
    
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="font-size: 1.5rem; margin: 0; color: #0052ff; font-weight: 600; letter-spacing: -0.02em;">Synapse-Lite</h1>
            <p style="color: #5b616e; font-size: 0.875rem; margin: 0.5rem 0; font-weight: 400;">Fraud Detection System</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation menu
        selected_page = st.radio("", list(PAGES.keys()), index=0)
        page_selection = PAGES[selected_page]
        
        st.markdown("---")
        
        # System Status
        st.markdown("### System Status")
        st.markdown(create_status_indicator("live", "Monitoring Active"), unsafe_allow_html=True)
        st.markdown(create_status_indicator("warning", "5 Alerts Pending"), unsafe_allow_html=True)
        st.markdown(create_status_indicator("live", "API Connected"), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick Stats
        st.markdown("### Quick Stats")
        metrics = {
            "transactions_today": random.randint(1000, 5000),
            "alerts_today": random.randint(10, 50),
            "risk_score": random.uniform(50, 80)
        }
        
        st.markdown(f"""
        <div style="font-size: 0.9rem; color: #a0aec0;">
            <p>Transactions Today: <strong style="color: #63b3ed;">{metrics['transactions_today']}</strong></p>
            <p>Alerts Today: <strong style="color: #ed8936;">{metrics['alerts_today']}</strong></p>
            <p>Avg Risk Score: <strong style="color: #48bb78;">{metrics['risk_score']:.1f}%</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #718096; font-size: 0.8rem;">
            <p>© 2024 Synapse-Lite<br>Fraud Detection System</p>
        </div>
        """, unsafe_allow_html=True)
    
    return page_selection