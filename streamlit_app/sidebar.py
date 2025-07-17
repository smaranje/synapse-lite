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
    """Render the sidebar navigation and return selected page"""
    
    with st.sidebar:
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #f0f3f7; margin-bottom: 1rem;">
            <h1 style="color: #0052ff; font-size: 1.5rem; margin: 0; font-weight: 600;">
                🔷 Synapse-Lite
            </h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown("### Navigation")
        selected_page = st.radio(
            "Choose a page:",
            list(PAGES.keys()),
            format_func=lambda x: f"{PAGES[x]} {x}",
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # System status
        st.markdown("### System Status")
        
        # Mock status indicators
        neo4j_status = random.choice(["online", "online", "warning"])
        kafka_status = random.choice(["online", "online", "offline"]) 
        ai_status = random.choice(["online", "warning", "online"])
        
        st.markdown(create_status_indicator(neo4j_status, "Neo4j Database"), unsafe_allow_html=True)
        st.markdown(create_status_indicator(kafka_status, "Kafka Stream"), unsafe_allow_html=True)
        st.markdown(create_status_indicator(ai_status, "AI Service"), unsafe_allow_html=True)
        
        st.markdown("---")
        
    return selected_page