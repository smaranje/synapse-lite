# Dashboard page module - Coinbase Business Style

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
from styling import create_metric_card, create_dashboard_header, create_quick_actions, create_alert_card

def render_dashboard():
    """Render the main dashboard page in Coinbase Business style"""
    
    # Generate system metrics
    metrics = generate_system_metrics()
    
    # Calculate total balance (portfolio value)
    total_balance = metrics['total_transactions_today'] * 125.50  # Simulate portfolio value
    balance_change = "$394.24 1D"
    
    # Coinbase-style dashboard header with balance
    st.markdown(create_dashboard_header(total_balance, balance_change), unsafe_allow_html=True)
    
    # Main layout with sidebar for quick actions
    col_main, col_sidebar = st.columns([3, 1])
    
    with col_main:
        # Portfolio allocation cards
        st.markdown("## Portfolio")
        
        # Key metrics in a 2x2 grid
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                create_metric_card(
                    "Fraud Detection", 
                    f"{metrics['fraud_alerts_today']}", 
                    "+12.3%"
                ), 
                unsafe_allow_html=True
            )
            
        with col2:
            st.markdown(
                create_metric_card(
                    "System Uptime", 
                    f"{metrics['system_uptime']:.1f}%", 
                    "+0.1%"
                ), 
                unsafe_allow_html=True
            )
            
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown(
                create_metric_card(
                    "Transactions Today", 
                    f"{metrics['total_transactions_today']:,}", 
                    "+5.2%"
                ), 
                unsafe_allow_html=True
            )
            
        with col4:
            st.markdown(
                create_metric_card(
                    "Processing Speed", 
                    f"{metrics['avg_processing_speed_ms']:.0f}ms", 
                    "-2.1%"
                ), 
                unsafe_allow_html=True
            )
        
        # Charts section
        st.markdown("## Analytics")
        
        # Charts in card containers
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown('<div class="cb-chart-container">', unsafe_allow_html=True)
            st.subheader("Hourly Transaction Volume")
            hourly_chart = create_hourly_volume_chart()
            if hourly_chart:
                st.plotly_chart(hourly_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_chart2:
            st.markdown('<div class="cb-chart-container">', unsafe_allow_html=True)
            st.subheader("Risk Distribution")
            risk_chart = create_risk_distribution_pie()
            if risk_chart:
                st.plotly_chart(risk_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional charts row
        col_chart3, col_chart4 = st.columns(2)
        
        with col_chart3:
            st.markdown('<div class="cb-chart-container">', unsafe_allow_html=True)
            st.subheader("Risk Trend Analysis")
            trend_chart = create_risk_trend_chart()
            if trend_chart:
                st.plotly_chart(trend_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_chart4:
            st.markdown('<div class="cb-chart-container">', unsafe_allow_html=True)
            st.subheader("Alert Volume")
            alert_chart = create_alert_volume_chart()
            if alert_chart:
                st.plotly_chart(alert_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col_sidebar:
        # Quick actions panel (Coinbase-style)
        st.markdown("## Quick actions")
        
        # Custom fraud detection actions
        st.markdown("""
        <div class="cb-quick-actions">
            <a href="#" class="cb-action-btn">
                <div class="cb-action-icon">🔍</div>
                <span>Manual Review</span>
            </a>
            <a href="#" class="cb-action-btn">
                <div class="cb-action-icon">⚙️</div>
                <span>Configure Rules</span>
            </a>
            <a href="#" class="cb-action-btn">
                <div class="cb-action-icon">📊</div>
                <span>Export Report</span>
            </a>
            <a href="#" class="cb-action-btn">
                <div class="cb-action-icon">🔔</div>
                <span>Alert Settings</span>
            </a>
            <a href="#" class="cb-action-btn">
                <div class="cb-action-icon">📈</div>
                <span>View Analytics</span>
            </a>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # System status
        st.markdown("## System Status")
        
        # Status indicators
        if metrics['system_uptime'] > 99.5:
            status_color = "green"
            status_text = "All systems operational"
            status_desc = "Fraud detection running smoothly"
        elif metrics['system_uptime'] > 95:
            status_color = "yellow"
            status_text = "Minor issues detected"
            status_desc = "Some delays in processing"
        else:
            status_color = "red"
            status_text = "System issues"
            status_desc = "Please check system status"
        
        st.markdown(f"""
        <div class="cb-card">
            <div class="cb-status-indicator">
                <div class="cb-status-dot {'online' if status_color == 'green' else 'warning' if status_color == 'yellow' else 'error'}"></div>
                <strong>{status_text}</strong>
            </div>
            <div style="margin-top: 0.5rem; color: var(--cb-gray-600); font-size: var(--cb-font-size-sm);">
                {status_desc}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Recent alerts
        st.markdown("## Recent Alerts")
        
        if metrics['fraud_alerts_today'] > 10:
            st.markdown(
                create_alert_card(
                    "High Alert Volume", 
                    f"{metrics['fraud_alerts_today']} alerts today", 
                    "warning"
                ), 
                unsafe_allow_html=True
            )
        elif metrics['fraud_alerts_today'] > 5:
            st.markdown(
                create_alert_card(
                    "Normal Activity", 
                    f"{metrics['fraud_alerts_today']} alerts today", 
                    "info"
                ), 
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                create_alert_card(
                    "Low Activity", 
                    f"{metrics['fraud_alerts_today']} alerts today", 
                    "success"
                ), 
                unsafe_allow_html=True
            )