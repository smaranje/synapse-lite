"""
Overview Page for Synapse-Lite
Main dashboard with key metrics and system overview
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd

class OverviewPage:
    """Overview page implementation"""
    
    def __init__(self, app_state):
        self.app_state = app_state
    
    def render(self):
        """Render the overview page"""
        # Get fresh data
        if self.app_state.should_refresh_data():
            self.app_state.refresh_data()
        
        # Render page sections
        self._render_key_metrics()
        self._render_charts_section()
        self._render_recent_activity()
        self._render_system_health()
    
    def _render_key_metrics(self):
        """Render key performance metrics"""
        st.markdown("## 📊 Key Metrics")
        
        # Get data
        from data.data_service import DataService
        data_service = DataService()
        
        transaction_stats = data_service.get_transaction_statistics()
        alert_stats = data_service.get_alert_statistics()
        system_metrics = data_service.get_system_metrics()
        
        # Create metrics grid
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
                <div class="metric-card">
                    <div class="metric-label">Transactions Today</div>
                    <div class="metric-value">{:,}</div>
                    <div class="metric-delta positive">+{:.1f}M USD Volume</div>
                </div>
            """.format(
                transaction_stats.get('total_transactions', 0),
                transaction_stats.get('total_volume_usd', 0) / 1_000_000
            ), unsafe_allow_html=True)
        
        with col2:
            high_risk_pct = transaction_stats.get('high_risk_percentage', 0)
            delta_class = "negative" if high_risk_pct > 5 else "positive"
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">High Risk Transactions</div>
                    <div class="metric-value">{transaction_stats.get('high_risk_transactions', 0):,}</div>
                    <div class="metric-delta {delta_class}">{high_risk_pct:.1f}% of total</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            active_alerts = alert_stats.get('active_alerts', 0)
            delta_class = "negative" if active_alerts > 10 else "positive"
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Active Alerts</div>
                    <div class="metric-value">{active_alerts}</div>
                    <div class="metric-delta {delta_class}">{alert_stats.get('resolution_rate', 0):.1f}% resolved</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            accuracy = system_metrics.get('detection_accuracy', 0)
            delta_class = "positive" if accuracy > 95 else "negative"
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Detection Accuracy</div>
                    <div class="metric-value">{accuracy:.1f}%</div>
                    <div class="metric-delta {delta_class}">AI Model Performance</div>
                </div>
            """, unsafe_allow_html=True)
    
    def _render_charts_section(self):
        """Render charts and visualizations"""
        st.markdown("## 📈 Analytics Overview")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self._render_volume_chart()
        
        with col2:
            self._render_risk_distribution_chart()
    
    def _render_volume_chart(self):
        """Render transaction volume chart"""
        from data.data_service import DataService
        data_service = DataService()
        
        # Get volume data
        volume_data = data_service.get_transaction_volume_data('24h')
        
        # Create the chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=volume_data['hours'],
            y=volume_data['volumes'],
            mode='lines+markers',
            name='Volume (USD)',
            line=dict(color='#0052ff', width=3),
            marker=dict(size=6),
            hovertemplate='<b>%{x}</b><br>Volume: $%{y:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Transaction Volume (24 Hours)",
            xaxis_title="Time",
            yaxis_title="Volume (USD)",
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_risk_distribution_chart(self):
        """Render risk distribution pie chart"""
        from data.data_service import DataService
        data_service = DataService()
        
        risk_analytics = data_service.get_risk_analytics()
        risk_dist = risk_analytics['risk_distribution']
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=['Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk'],
            values=[risk_dist['low'], risk_dist['medium'], risk_dist['high'], risk_dist['critical']],
            hole=0.4,
            marker_colors=['#00d924', '#ff9500', '#ff4757', '#dc143c']
        )])
        
        fig.update_layout(
            title="Risk Distribution",
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=400,
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_recent_activity(self):
        """Render recent activity section"""
        st.markdown("## 🕒 Recent Activity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Recent Alerts")
            alerts = self.app_state.get_alerts_data()[:5]  # Last 5 alerts
            
            if alerts:
                for alert in alerts:
                    severity = alert.get('severity', 'low')
                    severity_colors = {
                        'low': 'var(--info)',
                        'medium': 'var(--warning)', 
                        'high': 'var(--error)',
                        'critical': 'var(--accent-red)'
                    }
                    
                    timestamp = datetime.fromisoformat(alert.get('timestamp', ''))
                    time_str = timestamp.strftime('%H:%M')
                    
                    st.markdown(f"""
                        <div class="alert-card {severity}">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>{alert.get('type', 'Unknown Alert')}</strong><br>
                                    <small style="color: var(--secondary-text);">{alert.get('description', '')[:50]}...</small>
                                </div>
                                <div style="text-align: right;">
                                    <span class="status-badge status-{alert.get('status', 'active')}">{alert.get('status', 'active').title()}</span><br>
                                    <small style="color: var(--secondary-text);">{time_str}</small>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent alerts")
        
        with col2:
            st.markdown("### High-Risk Transactions")
            transactions = self.app_state.get_transactions_data()
            high_risk_txns = [t for t in transactions if t.get('risk_score', 0) > 80][:5]
            
            if high_risk_txns:
                for txn in high_risk_txns:
                    timestamp = datetime.fromisoformat(txn.get('timestamp', ''))
                    time_str = timestamp.strftime('%H:%M')
                    
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>${txn.get('amount_usd', 0):,.2f}</strong><br>
                                    <small style="color: var(--secondary-text);">{txn.get('hash', '')[:16]}...</small>
                                </div>
                                <div style="text-align: right;">
                                    <span style="color: var(--error); font-weight: 600;">Risk: {txn.get('risk_score', 0)}</span><br>
                                    <small style="color: var(--secondary-text);">{time_str}</small>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No high-risk transactions")
    
    def _render_system_health(self):
        """Render system health status"""
        st.markdown("## 🏥 System Health")
        
        col1, col2, col3 = st.columns(3)
        
        # Get performance metrics
        from data.data_service import DataService
        data_service = DataService()
        perf_metrics = data_service.get_performance_metrics()
        realtime_data = data_service.get_realtime_data()
        
        with col1:
            st.markdown("### Performance")
            
            # API Response Time
            response_time = perf_metrics.get('api_response_time_ms', 0)
            response_color = "green" if response_time < 100 else "orange" if response_time < 200 else "red"
            st.metric("API Response", f"{response_time:.0f}ms", help="Average API response time")
            
            # Memory Usage
            memory_usage = perf_metrics.get('memory_usage_mb', 0)
            st.metric("Memory Usage", f"{memory_usage:.0f}MB", help="Current memory consumption")
            
            # CPU Usage
            cpu_usage = perf_metrics.get('cpu_usage_percent', 0)
            st.metric("CPU Usage", f"{cpu_usage:.1f}%", help="Current CPU utilization")
        
        with col2:
            st.markdown("### Data Quality")
            
            # Cache Hit Rate
            cache_hit_rate = perf_metrics.get('cache_hit_rate', 0)
            st.metric("Cache Hit Rate", f"{cache_hit_rate:.1f}%", help="Percentage of cache hits")
            
            # Data Freshness
            data_freshness = perf_metrics.get('data_freshness_score', 0)
            st.metric("Data Freshness", f"{data_freshness:.1f}%", help="How fresh is our data")
            
            # Database Connections
            db_connections = perf_metrics.get('database_connections', 0)
            st.metric("DB Connections", f"{db_connections}", help="Active database connections")
        
        with col3:
            st.markdown("### Processing")
            
            # Transactions per Second
            tps = realtime_data.get('transactions_per_second', 0)
            st.metric("Transactions/sec", f"{tps:.1f}", help="Current processing rate")
            
            # Queue Size
            queue_size = realtime_data.get('queue_size', 0)
            st.metric("Queue Size", f"{queue_size}", help="Messages in processing queue")
            
            # Success Rate
            success_rate = realtime_data.get('success_rate', 0)
            st.metric("Success Rate", f"{success_rate:.1f}%", help="Transaction processing success rate")
        
        # System Status Summary
        st.markdown("### System Status Summary")
        
        status_col1, status_col2, status_col3 = st.columns(3)
        
        with status_col1:
            # Overall Health Score
            health_score = (
                (100 - cpu_usage) * 0.3 +
                min(cache_hit_rate, 100) * 0.3 +
                min(success_rate, 100) * 0.4
            )
            
            if health_score >= 90:
                health_status = "🟢 Excellent"
                health_color = "var(--success)"
            elif health_score >= 75:
                health_status = "🟡 Good"
                health_color = "var(--warning)"
            else:
                health_status = "🔴 Needs Attention"
                health_color = "var(--error)"
            
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Overall Health</div>
                    <div class="metric-value" style="color: {health_color};">{health_status}</div>
                    <div class="metric-delta">Score: {health_score:.1f}/100</div>
                </div>
            """, unsafe_allow_html=True)
        
        with status_col2:
            # System Uptime
            uptime_hours = self.app_state.get_system_metrics().get('uptime_hours', 0)
            uptime_days = uptime_hours / 24
            
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">System Uptime</div>
                    <div class="metric-value">{uptime_days:.1f} days</div>
                    <div class="metric-delta positive">99.9% availability</div>
                </div>
            """, unsafe_allow_html=True)
        
        with status_col3:
            # Last Maintenance
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Last Maintenance</div>
                    <div class="metric-value">3 days ago</div>
                    <div class="metric-delta">Next: In 4 days</div>
                </div>
            """, unsafe_allow_html=True)