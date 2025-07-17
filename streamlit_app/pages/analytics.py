"""
Analytics Page for Synapse-Lite
Advanced analytics, trends, and insights
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

class AnalyticsPage:
    """Analytics page implementation"""
    
    def __init__(self, app_state):
        self.app_state = app_state
    
    def render(self):
        """Render the analytics page"""
        self._render_analytics_header()
        self._render_key_insights()
        self._render_transaction_analytics()
        self._render_risk_analytics()
        self._render_geographic_analytics()
        self._render_trend_analysis()
    
    def _render_analytics_header(self):
        """Render analytics page header"""
        st.markdown("## 📈 Advanced Analytics")
        st.markdown("Deep insights into transaction patterns, risk trends, and system performance")
        
        # Time period selector
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            time_period = st.selectbox(
                "Analysis Period",
                ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
                index=1
            )
        
        with col2:
            comparison = st.checkbox("Compare with Previous Period", value=True)
        
        with col3:
            if st.button("🔄 Refresh Analytics"):
                self.app_state.refresh_data()
                st.rerun()
        
        st.session_state.analytics_period = time_period
        st.session_state.show_comparison = comparison
    
    def _render_key_insights(self):
        """Render key insights and KPIs"""
        st.markdown("### 🎯 Key Insights")
        
        from data.data_service import DataService
        data_service = DataService()
        
        # Get analytics data
        transaction_stats = data_service.get_transaction_statistics()
        alert_stats = data_service.get_alert_statistics()
        risk_analytics = data_service.get_risk_analytics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Detection efficiency
            efficiency = transaction_stats.get('high_risk_percentage', 0)
            efficiency_delta = "+0.3%" if efficiency < 5 else "-0.2%"
            st.metric(
                "Detection Efficiency",
                f"{efficiency:.1f}%",
                delta=efficiency_delta,
                help="Percentage of high-risk transactions detected"
            )
        
        with col2:
            # False positive rate
            fp_rate = alert_stats.get('resolution_rate', 0)
            fp_delta = "-0.5%" if fp_rate > 90 else "+0.2%"
            st.metric(
                "Accuracy Score",
                f"{fp_rate:.1f}%",
                delta=fp_delta,
                help="Alert resolution accuracy"
            )
        
        with col3:
            # Volume growth
            volume_growth = "+12.3%"
            st.metric(
                "Volume Growth",
                volume_growth,
                delta="vs last period",
                help="Transaction volume growth"
            )
        
        with col4:
            # Risk trend
            avg_risk = risk_analytics.get('trend_data', {}).get('risk_scores', [0])[-1] if risk_analytics.get('trend_data', {}).get('risk_scores') else 0
            risk_delta = "-2.1" if avg_risk < 35 else "+1.5"
            st.metric(
                "Avg Risk Score",
                f"{avg_risk:.1f}",
                delta=risk_delta,
                help="Average risk score trend"
            )
    
    def _render_transaction_analytics(self):
        """Render transaction analytics"""
        st.markdown("### 💰 Transaction Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_volume_trend_chart()
        
        with col2:
            self._render_transaction_size_distribution()
        
        # Additional transaction metrics
        col3, col4 = st.columns(2)
        
        with col3:
            self._render_hourly_pattern()
        
        with col4:
            self._render_status_breakdown()
    
    def _render_volume_trend_chart(self):
        """Render transaction volume trend"""
        from data.data_service import DataService
        data_service = DataService()
        
        volume_data = data_service.get_transaction_volume_data('7d')
        
        fig = go.Figure()
        
        # Current period
        fig.add_trace(go.Scatter(
            x=volume_data['dates'],
            y=volume_data['volumes'],
            mode='lines+markers',
            name='Transaction Volume',
            line=dict(color='#0052ff', width=3),
            marker=dict(size=8)
        ))
        
        # Add comparison period if enabled
        if st.session_state.get('show_comparison', False):
            # Generate mock comparison data
            comparison_volumes = [v * 0.85 for v in volume_data['volumes']]
            fig.add_trace(go.Scatter(
                x=volume_data['dates'],
                y=comparison_volumes,
                mode='lines',
                name='Previous Period',
                line=dict(color='#888888', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title="Transaction Volume Trend",
            xaxis_title="Date",
            yaxis_title="Volume (USD)",
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_transaction_size_distribution(self):
        """Render transaction size distribution"""
        # Generate sample distribution data
        import numpy as np
        
        # Simulate transaction sizes (log-normal distribution)
        np.random.seed(42)
        sizes = np.random.lognormal(mean=2, sigma=1.5, size=1000)
        
        fig = px.histogram(
            x=sizes,
            nbins=30,
            title="Transaction Size Distribution",
            labels={'x': 'Transaction Size (USD)', 'y': 'Frequency'},
            marginal="box"
        )
        
        fig.update_layout(
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_hourly_pattern(self):
        """Render hourly transaction patterns"""
        from data.data_service import DataService
        data_service = DataService()
        
        volume_data = data_service.get_transaction_volume_data('24h')
        
        # Convert hours to numbers for better visualization
        hours_numeric = list(range(24))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hours_numeric,
            y=volume_data['transaction_counts'],
            mode='lines+markers',
            fill='tonexty',
            name='Transaction Count',
            line=dict(color='#00d924', width=2)
        ))
        
        fig.update_layout(
            title="24-Hour Transaction Pattern",
            xaxis_title="Hour of Day",
            yaxis_title="Transaction Count",
            xaxis=dict(tickmode='linear', tick0=0, dtick=4),
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_status_breakdown(self):
        """Render transaction status breakdown"""
        # Mock status data
        status_data = {
            'Confirmed': 85,
            'Pending': 10,
            'Flagged': 3,
            'Review': 2
        }
        
        fig = px.pie(
            values=list(status_data.values()),
            names=list(status_data.keys()),
            title="Transaction Status Breakdown",
            color_discrete_map={
                'Confirmed': '#00d924',
                'Pending': '#ff9500',
                'Flagged': '#ff4757',
                'Review': '#ffa502'
            }
        )
        
        fig.update_layout(
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_risk_analytics(self):
        """Render risk analytics section"""
        st.markdown("### ⚠️ Risk Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_risk_score_trends()
        
        with col2:
            self._render_detection_methods()
        
        # Risk factors analysis
        self._render_risk_factors_analysis()
    
    def _render_risk_score_trends(self):
        """Render risk score trends over time"""
        from data.data_service import DataService
        data_service = DataService()
        
        risk_analytics = data_service.get_risk_analytics()
        trend_data = risk_analytics.get('trend_data', {})
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_data.get('dates', []),
            y=trend_data.get('risk_scores', []),
            mode='lines+markers',
            name='Average Risk Score',
            line=dict(color='#ff4757', width=3),
            marker=dict(size=8)
        ))
        
        # Add threshold line
        fig.add_hline(
            y=50, 
            line_dash="dash", 
            line_color="orange",
            annotation_text="Alert Threshold"
        )
        
        fig.update_layout(
            title="Risk Score Trends",
            xaxis_title="Date",
            yaxis_title="Average Risk Score",
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_detection_methods(self):
        """Render detection methods breakdown"""
        from data.data_service import DataService
        data_service = DataService()
        
        risk_analytics = data_service.get_risk_analytics()
        detection_methods = risk_analytics.get('detection_methods', {})
        
        fig = px.bar(
            x=list(detection_methods.keys()),
            y=list(detection_methods.values()),
            title="Detection Methods Performance",
            labels={'x': 'Detection Method', 'y': 'Alerts Generated'},
            color=list(detection_methods.values()),
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=350,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_risk_factors_analysis(self):
        """Render risk factors analysis"""
        st.markdown("#### Risk Factors Analysis")
        
        # Mock risk factors data
        risk_factors = {
            'Multiple small transactions': 25,
            'Geographic anomaly': 20,
            'Velocity threshold exceeded': 18,
            'Suspicious wallet clustering': 15,
            'Round amount pattern': 12,
            'High-frequency trading': 10
        }
        
        # Create horizontal bar chart
        fig = px.bar(
            x=list(risk_factors.values()),
            y=list(risk_factors.keys()),
            orientation='h',
            title="Top Risk Factors (Last 7 Days)",
            labels={'x': 'Frequency', 'y': 'Risk Factor'}
        )
        
        fig.update_layout(
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_geographic_analytics(self):
        """Render geographic analytics"""
        st.markdown("### 🌍 Geographic Analytics")
        
        from data.data_service import DataService
        data_service = DataService()
        geo_data = data_service.get_geographic_data()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Geographic heatmap
            df_geo = pd.DataFrame(geo_data)
            
            fig = px.scatter_geo(
                df_geo,
                lat='latitude',
                lon='longitude',
                size='transaction_count',
                color='avg_risk_score',
                hover_name='country',
                hover_data=['total_volume_usd', 'high_risk_count'],
                title="Global Transaction Activity",
                color_continuous_scale='RdYlBu_r'
            )
            
            fig.update_layout(
                template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
                height=400,
                geo=dict(showframe=False, showcoastlines=True)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top countries by risk
            st.markdown("#### Highest Risk Countries")
            
            # Sort by risk score
            sorted_countries = sorted(geo_data, key=lambda x: x['avg_risk_score'], reverse=True)[:5]
            
            for i, country_data in enumerate(sorted_countries):
                risk_score = country_data['avg_risk_score']
                risk_color = self._get_risk_color(risk_score)
                
                st.markdown(f"""
                    <div class="metric-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{country_data['country']}</strong><br>
                                <small>{country_data['transaction_count']:,} transactions</small>
                            </div>
                            <div style="text-align: right;">
                                <span style="color: {risk_color}; font-weight: 600;">{risk_score:.1f}</span><br>
                                <small>Risk Score</small>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    def _render_trend_analysis(self):
        """Render trend analysis section"""
        st.markdown("### 📊 Trend Analysis")
        
        # Create comprehensive trend dashboard
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Transaction Volume', 'Alert Frequency', 'Processing Time', 'System Load'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Mock time series data
        import numpy as np
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        
        # Transaction volume trend
        volume_trend = np.random.normal(100000, 20000, 30).cumsum()
        fig.add_trace(
            go.Scatter(x=dates, y=volume_trend, name='Volume', line=dict(color='#0052ff')),
            row=1, col=1
        )
        
        # Alert frequency
        alert_trend = np.random.poisson(5, 30)
        fig.add_trace(
            go.Scatter(x=dates, y=alert_trend, name='Alerts', line=dict(color='#ff4757')),
            row=1, col=2
        )
        
        # Processing time
        processing_trend = np.random.exponential(50, 30)
        fig.add_trace(
            go.Scatter(x=dates, y=processing_trend, name='Processing Time', line=dict(color='#00d924')),
            row=2, col=1
        )
        
        # System load
        load_trend = np.random.normal(70, 10, 30)
        fig.add_trace(
            go.Scatter(x=dates, y=load_trend, name='System Load', line=dict(color='#ff9500')),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            title_text="30-Day Trend Analysis"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend insights
        self._render_trend_insights()
    
    def _render_trend_insights(self):
        """Render trend insights"""
        st.markdown("#### 💡 Trend Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                **📈 Volume Trends**
                - 12% increase in transaction volume
                - Peak activity during 14:00-16:00 UTC
                - Weekend volumes 30% lower
                - Largest transactions from US, UK, Germany
            """)
        
        with col2:
            st.markdown("""
                **⚠️ Risk Patterns**
                - Geographic anomalies up 8%
                - Velocity patterns most common risk factor
                - False positive rate decreased 15%
                - AI model accuracy at 96.8%
            """)
        
        with col3:
            st.markdown("""
                **🎯 Performance**
                - Average processing time: 45ms
                - System uptime: 99.9%
                - Alert resolution time improved 20%
                - Detection accuracy increased 2.3%
            """)
    
    def _get_risk_color(self, risk_score):
        """Get color based on risk score"""
        if risk_score >= 80:
            return "var(--error)"
        elif risk_score >= 60:
            return "var(--warning)"
        elif risk_score >= 40:
            return "var(--accent-orange)"
        else:
            return "var(--success)"