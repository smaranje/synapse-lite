# Dashboard page module

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_generator import generate_system_metrics
from charts import (
    create_hourly_volume_chart, 
    create_risk_distribution_pie,
    create_risk_trend_chart,
    create_alert_volume_chart
)
from styling import create_metric_card

def render_dashboard():
    """Render the main dashboard page"""
    st.title("🏠 Dashboard")
    st.markdown("### Real-time Fraud Detection Overview")
    
    # Generate system metrics
    metrics = generate_system_metrics()
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Transactions Today", 
            f"{metrics['total_transactions_today']:,}", 
            "+5.2%"
        )
    
    with col2:
        st.metric(
            "Fraud Alerts", 
            str(metrics['fraud_alerts_today']), 
            "+12%"
        )
    
    with col3:
        st.metric(
            "System Uptime", 
            f"{metrics['system_uptime']:.1f}%", 
            "0%"
        )
    
    with col4:
        st.metric(
            "Detection Accuracy", 
            f"{metrics['detection_accuracy']:.1f}%", 
            "+2.1%"
        )
    
    st.markdown("---")
    
    # Charts section
    st.markdown("## Real-time Analytics")
    
    # Main charts row
    chart_col1, chart_col2 = st.columns([2, 1])
    
    with chart_col1:
        st.subheader("Transaction Volume (24h)")
        fig_volume = create_hourly_volume_chart()
        st.plotly_chart(fig_volume, use_container_width=True)
    
    with chart_col2:
        st.subheader("Risk Distribution")
        fig_risk_pie = create_risk_distribution_pie()
        st.plotly_chart(fig_risk_pie, use_container_width=True)
    
    # Secondary charts row
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.subheader("Risk Score Trend")
        fig_risk_trend = create_risk_trend_chart()
        st.plotly_chart(fig_risk_trend, use_container_width=True)
    
    with chart_col4:
        st.subheader("Alert Volume")
        fig_alerts = create_alert_volume_chart()
        st.plotly_chart(fig_alerts, use_container_width=True)
    
    st.markdown("---")
    
    # System performance metrics
    st.markdown("## System Performance")
    
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    with perf_col1:
        st.markdown(
            create_metric_card(
                "Processing Speed", 
                f"{metrics['processing_speed']} tx/min",
                "+8.2%",
                "normal"
            ), 
            unsafe_allow_html=True
        )
    
    with perf_col2:
        st.markdown(
            create_metric_card(
                "API Response Time", 
                f"{metrics['api_response_time']:.0f}ms",
                "-12ms",
                "inverse"
            ), 
            unsafe_allow_html=True
        )
    
    with perf_col3:
        st.markdown(
            create_metric_card(
                "Active Users", 
                str(metrics['active_users']),
                "+15",
                "normal"
            ), 
            unsafe_allow_html=True
        )
    
    with perf_col4:
        st.markdown(
            create_metric_card(
                "DB Connections", 
                str(metrics['database_connections']),
                "Healthy",
                "normal"
            ), 
            unsafe_allow_html=True
        )
    
    # Live status indicators
    st.markdown("---")
    st.markdown("## System Status")
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.markdown("""
        <div style="padding: 1rem; background: white; border-radius: 8px; border: 1px solid #f0f3f7;">
            <h4 style="margin: 0 0 0.5rem 0; color: #1a1a1a;">Data Pipeline</h4>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #059669;"></div>
                <span style="color: #059669; font-weight: 500;">Operational</span>
            </div>
            <small style="color: #6b7280;">Last update: 2 seconds ago</small>
        </div>
        """, unsafe_allow_html=True)
    
    with status_col2:
        st.markdown("""
        <div style="padding: 1rem; background: white; border-radius: 8px; border: 1px solid #f0f3f7;">
            <h4 style="margin: 0 0 0.5rem 0; color: #1a1a1a;">ML Models</h4>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #059669;"></div>
                <span style="color: #059669; font-weight: 500;">Active</span>
            </div>
            <small style="color: #6b7280;">Model v2.1.3 deployed</small>
        </div>
        """, unsafe_allow_html=True)
    
    with status_col3:
        st.markdown("""
        <div style="padding: 1rem; background: white; border-radius: 8px; border: 1px solid #f0f3f7;">
            <h4 style="margin: 0 0 0.5rem 0; color: #1a1a1a;">Alert System</h4>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: #ea580c;"></div>
                <span style="color: #ea580c; font-weight: 500;">5 Pending</span>
            </div>
            <small style="color: #6b7280;">Requires attention</small>
        </div>
        """, unsafe_allow_html=True)