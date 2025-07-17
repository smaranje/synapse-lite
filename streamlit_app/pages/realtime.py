"""
Real-time Monitor Page for Synapse-Lite
Live transaction monitoring and system status
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime

class RealtimePage:
    """Real-time monitoring page implementation"""
    
    def __init__(self, app_state):
        self.app_state = app_state
    
    def render(self):
        """Render the real-time monitoring page"""
        self._render_realtime_header()
        self._render_live_metrics()
        self._render_transaction_stream()
        self._render_system_monitoring()
    
    def _render_realtime_header(self):
        """Render real-time page header with controls"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("## 📊 Real-time Monitor")
            st.markdown("Live Bitcoin transaction monitoring and system status")
        
        with col2:
            auto_refresh = st.checkbox("Auto Refresh", value=True, help="Automatically refresh data")
            if auto_refresh:
                time.sleep(2)
                st.rerun()
        
        with col3:
            if st.button("🔄 Refresh Now", use_container_width=True):
                self.app_state.refresh_data()
                st.rerun()
    
    def _render_live_metrics(self):
        """Render live system metrics"""
        from data.data_service import DataService
        data_service = DataService()
        realtime_data = data_service.get_realtime_data()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            tps = realtime_data.get('transactions_per_second', 0)
            st.metric("TPS", f"{tps:.1f}", help="Transactions per second")
        
        with col2:
            load = realtime_data.get('current_load', 0)
            load_delta = f"+{load-70}%" if load > 70 else f"{load-70}%"
            st.metric("System Load", f"{load}%", delta=load_delta)
        
        with col3:
            connections = realtime_data.get('active_connections', 0)
            st.metric("Connections", f"{connections}", help="Active connections")
        
        with col4:
            latency = realtime_data.get('processing_latency_ms', 0)
            st.metric("Latency", f"{latency:.1f}ms", help="Processing latency")
        
        with col5:
            queue_size = realtime_data.get('queue_size', 0)
            queue_delta = "⚠️" if queue_size > 50 else "✅"
            st.metric("Queue", f"{queue_size}", delta=queue_delta)
    
    def _render_transaction_stream(self):
        """Render live transaction stream"""
        st.markdown("## 💰 Live Transaction Stream")
        
        # Get recent transactions
        transactions = self.app_state.get_transactions_data()[:10]
        
        if transactions:
            # Create a container for the stream
            stream_container = st.container()
            
            with stream_container:
                for i, txn in enumerate(transactions):
                    risk_score = txn.get('risk_score', 0)
                    
                    # Color coding based on risk
                    if risk_score > 80:
                        risk_color = "var(--error)"
                        risk_icon = "🔴"
                    elif risk_score > 60:
                        risk_color = "var(--warning)"
                        risk_icon = "🟡"
                    else:
                        risk_color = "var(--success)"
                        risk_icon = "🟢"
                    
                    timestamp = datetime.fromisoformat(txn.get('timestamp', ''))
                    time_str = timestamp.strftime('%H:%M:%S')
                    
                    # Create animated transaction card
                    st.markdown(f"""
                        <div class="metric-card animate-in" style="animation-delay: {i*0.1}s;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="flex: 1;">
                                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                                        <span style="font-size: 1.2rem;">{risk_icon}</span>
                                        <strong style="color: var(--primary-text);">${txn.get('amount_usd', 0):,.2f}</strong>
                                        <span style="color: {risk_color}; font-weight: 600;">Risk: {risk_score}</span>
                                    </div>
                                    <div style="margin-top: 0.25rem; font-size: 0.8rem; color: var(--secondary-text);">
                                        {txn.get('hash', '')[:24]}... • {txn.get('country', 'Unknown')}
                                    </div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 0.8rem; color: var(--secondary-text);">{time_str}</div>
                                    <div style="font-size: 0.7rem; color: var(--secondary-text);">{txn.get('status', 'pending').title()}</div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No recent transactions to display")
    
    def _render_system_monitoring(self):
        """Render system monitoring charts"""
        st.markdown("## 🖥️ System Monitoring")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_performance_gauge()
        
        with col2:
            self._render_alert_timeline()
    
    def _render_performance_gauge(self):
        """Render system performance gauge"""
        from data.data_service import DataService
        data_service = DataService()
        realtime_data = data_service.get_realtime_data()
        
        # Create gauge chart for system load
        load = realtime_data.get('current_load', 0)
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = load,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "System Load"},
            delta = {'reference': 70},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#0052ff"},
                'steps': [
                    {'range': [0, 70], 'color': "lightgray"},
                    {'range': [70, 85], 'color': "yellow"},
                    {'range': [85, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_alert_timeline(self):
        """Render recent alerts timeline"""
        alerts = self.app_state.get_alerts_data()[:5]
        
        if alerts:
            # Create timeline chart
            timestamps = []
            severities = []
            descriptions = []
            
            for alert in alerts:
                timestamp = datetime.fromisoformat(alert.get('timestamp', ''))
                timestamps.append(timestamp)
                severities.append(alert.get('severity', 'low'))
                descriptions.append(alert.get('type', 'Unknown'))
            
            # Color mapping for severities
            severity_colors = {
                'low': '#00d924',
                'medium': '#ff9500', 
                'high': '#ff4757',
                'critical': '#dc143c'
            }
            
            colors = [severity_colors.get(s, '#00d924') for s in severities]
            
            fig = go.Figure(data=go.Scatter(
                x=timestamps,
                y=list(range(len(timestamps))),
                mode='markers+text',
                marker=dict(
                    size=20,
                    color=colors,
                    symbol='circle'
                ),
                text=descriptions,
                textposition="middle right",
                hovertemplate='<b>%{text}</b><br>%{x}<br>Severity: %{marker.color}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Recent Alert Timeline",
                xaxis_title="Time",
                yaxis=dict(showticklabels=False, showgrid=False),
                template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
                height=300,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No recent alerts to display")
    
    def _render_realtime_stats(self):
        """Render additional real-time statistics"""
        st.markdown("## 📈 Real-time Statistics")
        
        from data.data_service import DataService
        data_service = DataService()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Processing Stats")
            realtime_data = data_service.get_realtime_data()
            
            success_rate = realtime_data.get('success_rate', 0)
            st.progress(success_rate / 100, text=f"Success Rate: {success_rate:.1f}%")
            
            accuracy = realtime_data.get('ai_model_accuracy', 0)
            st.progress(accuracy / 100, text=f"AI Accuracy: {accuracy:.1f}%")
        
        with col2:
            st.markdown("### Volume Trends")
            # Simple trend indicators
            st.metric("Hourly Volume", "$2.4M", delta="+15.2%")
            st.metric("Transaction Count", "8,342", delta="+234")
        
        with col3:
            st.markdown("### Risk Analysis")
            st.metric("Avg Risk Score", "34.2", delta="-2.1")
            st.metric("High Risk %", "4.7%", delta="-0.3%")