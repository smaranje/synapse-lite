"""
Dashboard page for the Synapse-Lite Fraud Detection System
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

def show():
    """Display the main dashboard page"""
    st.title("Fraud Detection Dashboard")
    
    # System status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="status-indicator-clean">
            <div class="status-dot"></div>
            <span>Monitoring Active</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="status-indicator-clean">
            <div class="status-dot"></div>
            <span>API Connected</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        alerts_pending = len([a for a in st.session_state.alerts if a['status'] == 'Open'])
        st.markdown(f"""
        <div class="status-indicator-clean">
            <div class="status-dot" style="background: {'#FF5252' if alerts_pending > 0 else '#00D395'}"></div>
            <span>{alerts_pending} Alerts Pending</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="status-indicator-clean">
            <span>Last Update: {st.session_state.last_refresh.strftime('%H:%M:%S')}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
    
    # Key metrics with Coinbase blue background
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tx = len(st.session_state.transactions)
        prev_total = int(total_tx * 0.88)  # Simulated previous value
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Total Transactions</div>
            <div class="kpi-value">{total_tx:,}</div>
            <div class="kpi-delta positive">+{total_tx - prev_total} from yesterday</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        active_alerts = len([a for a in st.session_state.alerts if a['status'] == 'Open'])
        critical_alerts = len([a for a in st.session_state.alerts if a['risk_level'] == 'Critical' and a['status'] == 'Open'])
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Active Alerts</div>
            <div class="kpi-value">{active_alerts}</div>
            <div class="kpi-delta">{critical_alerts} Critical</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_risk = np.mean([t['ml_score'] for t in st.session_state.transactions]) * 100 if st.session_state.transactions else 0
        prev_avg_risk = avg_risk * 0.92  # Simulated previous value
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Average Risk Score</div>
            <div class="kpi-value">{avg_risk:.1f}%</div>
            <div class="kpi-delta positive">+{avg_risk - prev_avg_risk:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        detection_rate = (len(st.session_state.alerts) / len(st.session_state.transactions)) * 100 if st.session_state.transactions else 0
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Detection Rate</div>
            <div class="kpi-value">{detection_rate:.1f}%</div>
            <div class="kpi-delta positive">+2.3%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts row
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("### Real-time Analytics")
    
    # Create three columns for charts
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Risk Score Trend (24h)
        st.subheader("Risk Score Trend (24h)")
        
        # Generate time series data
        time_data = []
        now = datetime.now()
        for i in range(24):
            hour_time = now - timedelta(hours=23-i)
            hour_transactions = [t for t in st.session_state.transactions 
                               if t['timestamp'].hour == hour_time.hour]
            if hour_transactions:
                avg_score = np.mean([t['ml_score'] for t in hour_transactions])
            else:
                avg_score = random.uniform(0.3, 0.7)
            
            time_data.append({
                'Time': hour_time,
                'Risk Score': avg_score * 100
            })
        
        df_trend = pd.DataFrame(time_data)
        
        fig = px.line(df_trend, x='Time', y='Risk Score', 
                     line_shape='spline', markers=True)
        fig.update_traces(line_color='#0052FF', line_width=3)
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Risk Score (%)",
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=300,
            xaxis=dict(
                showgrid=True, 
                gridcolor='rgba(128,128,128,0.2)',
                linecolor='rgba(128,128,128,0.4)',
                tickfont=dict(color='#5e6278')
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor='rgba(128,128,128,0.2)',
                linecolor='rgba(128,128,128,0.4)',
                tickfont=dict(color='#5e6278')
            ),
            font=dict(color='#050f19')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Transaction Volume (24h)
        st.subheader("Transaction Volume (24h)")
        
        # Generate hourly volume data
        volume_data = []
        for i in range(24):
            hour_time = now - timedelta(hours=23-i)
            hour_count = len([t for t in st.session_state.transactions 
                            if t['timestamp'].hour == hour_time.hour])
            volume_data.append({
                'Hour': hour_time.strftime('%H:00'),
                'Count': hour_count if hour_count > 0 else random.randint(2, 8)
            })
        
        df_volume = pd.DataFrame(volume_data)
        
        fig = px.bar(df_volume, x='Hour', y='Count')
        fig.update_traces(marker_color='#00D395')
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Transaction Count",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=300,
            xaxis=dict(
                showgrid=False,
                linecolor='rgba(128,128,128,0.4)',
                tickfont=dict(color='#5e6278')
            ),
            yaxis=dict(
                showgrid=True, 
                gridcolor='rgba(128,128,128,0.2)',
                linecolor='rgba(128,128,128,0.4)',
                tickfont=dict(color='#5e6278')
            ),
            font=dict(color='#050f19')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Alert Distribution
        st.subheader("Alert Distribution")
        
        risk_counts = pd.DataFrame([
            {'Risk Level': level, 'Count': len([a for a in st.session_state.alerts 
                                               if a['risk_level'] == level and a['status'] == 'Open'])}
            for level in ['Critical', 'High', 'Medium', 'Low']
        ])
        
        fig = px.pie(risk_counts, values='Count', names='Risk Level',
                    color_discrete_map={
                        'Critical': '#FF5252',
                        'High': '#FF9800',
                        'Medium': '#FFC107',
                        'Low': '#00D395'
                    })
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Recent Transactions")
        recent_tx = sorted(st.session_state.transactions, 
                          key=lambda x: x['timestamp'], reverse=True)[:5]
        
        for tx in recent_tx:
            risk_color = {
                'Critical': '#FF5252',
                'High': '#FF9800',
                'Medium': '#FFC107',
                'Low': '#00D395'
            }.get(tx['risk_level'], '#00D395')
            
            st.markdown(f"""
            <div class="transaction-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="tx-hash">{tx['hash'][:8]}...{tx['hash'][-6:]}</div>
                        <div class="tx-details">{tx['timestamp'].strftime('%H:%M:%S')} • {tx['total_value_btc']:.6f} BTC</div>
                    </div>
                    <div class="risk-badge-clean" data-risk="{tx['risk_level']}">
                        {tx['risk_level']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Recent Alerts")
        recent_alerts = sorted([a for a in st.session_state.alerts if a['status'] == 'Open'], 
                             key=lambda x: x['timestamp'], reverse=True)[:5]
        
        for alert in recent_alerts:
            risk_color = {
                'Critical': '#FF5252',
                'High': '#FF9800',
                'Medium': '#FFC107',
                'Low': '#00D395'
            }.get(alert['risk_level'], '#00D395')
            
            st.markdown(f"""
            <div class="transaction-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="tx-hash">{alert['alert_id']}</div>
                        <div class="tx-details">{alert['description'][:50]}...</div>
                        <div class="tx-details">{alert['timestamp'].strftime('%H:%M:%S')} • ${alert['total_value_usd']:,.2f}</div>
                    </div>
                    <div class="risk-badge-clean" data-risk="{alert['risk_level']}">
                        {alert['risk_level']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)