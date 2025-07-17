"""Dashboard page for the fraud detection system."""

import streamlit as st
import random

def render_dashboard():
    """Render the main dashboard page."""
    st.markdown("# Fraud Detection Dashboard")
    st.markdown("### Real-time Bitcoin transaction monitoring and threat analysis")
    
    # Status indicator
    st.markdown('<span class="status-indicator status-live">● Live Monitoring Active</span>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Enhanced metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Transactions</div>
            <div class="metric-value">2,847</div>
            <div class="metric-delta positive">+12% from yesterday</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Active Alerts</div>
            <div class="metric-value">23</div>
            <div class="metric-delta negative">5 Critical</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Risk Score</div>
            <div class="metric-value">67.3%</div>
            <div class="metric-delta neutral">+2.1% from avg</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Detection Rate</div>
            <div class="metric-value">94.2%</div>
            <div class="metric-delta positive">Above target</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts section placeholder
    st.markdown("## Real-time Analytics")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.info("📈 Risk Score Trend Chart")
        st.markdown("*Chart will load when data generator is available*")
    
    with chart_col2:
        st.info("📊 Transaction Volume Chart") 
        st.markdown("*Chart will load when data generator is available*")
    
    st.info("🥧 Alert Distribution Chart")
    st.markdown("*Chart will load when data generator is available*")
    
    st.markdown("---")
    
    # Recent transactions and alerts placeholder
    recent_col1, recent_col2 = st.columns(2)
    
    with recent_col1:
        st.markdown("## Recent Transactions")
        st.markdown("""
        <div class="transaction-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>abc123def456...</strong><br>
                    <small style="color: #a0aec0;">0.0045 BTC</small>
                </div>
                <div><span class="risk-badge medium">Medium (65%)</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with recent_col2:
        st.markdown("## Recent Alerts")
        st.markdown("""
        <div class="alert-card high">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>xyz789uvw012...</strong><br>
                    <small style="color: #a0aec0;">15:23:45</small>
                </div>
                <div><span class="risk-badge high">High (85%)</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)