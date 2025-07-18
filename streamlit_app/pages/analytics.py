"""
Analytics page for the Synapse-Lite Fraud Detection System
Provides deep insights into fraud patterns and system performance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from utils import service_integration

def show():
    """Display the analytics page"""
    st.title("📊 Analytics Dashboard")
    
    # Time range selector
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        time_range = st.select_slider(
            "Select Time Range",
            options=["1H", "6H", "12H", "24H", "7D", "30D"],
            value="24H",
            key="time_range"
        )
    
    with col2:
        chart_theme = st.selectbox(
            "Chart Theme",
            ["plotly", "plotly_white", "plotly_dark"],
            index=1,
            key="chart_theme"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Analytics"):
            st.rerun()
    
    # Get analytics data
    if not st.session_state.USE_DUMMY_DATA:
        neo4j_conn = service_integration.get_neo4j_connection()
        analytics_data = neo4j_conn.get_analytics_data()
    else:
        # Use data from session state for analytics
        analytics_data = {
            'total_transactions': len(st.session_state.transactions),
            'avg_risk_score': np.mean([t['ml_score'] for t in st.session_state.transactions]),
            'total_volume': sum(t['total_value_btc'] for t in st.session_state.transactions),
            'avg_transaction_size': np.mean([t['total_value_btc'] for t in st.session_state.transactions])
        }
    
    # Key Statistics Section
    st.markdown("### 📈 Key Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Transactions",
            f"{analytics_data.get('total_transactions', 0):,}",
            help="Total number of transactions analyzed"
        )
    
    with col2:
        st.metric(
            "Average Risk Score",
            f"{analytics_data.get('avg_risk_score', 0):.2%}",
            help="Average ML fraud score across all transactions"
        )
    
    with col3:
        st.metric(
            "Total Volume",
            f"{analytics_data.get('total_volume', 0):.2f} BTC",
            f"${analytics_data.get('total_volume', 0) * 45000:,.0f}",
            help="Total transaction volume processed"
        )
    
    with col4:
        st.metric(
            "Avg Transaction Size",
            f"{analytics_data.get('avg_transaction_size', 0):.4f} BTC",
            help="Average transaction size"
        )
    
    st.markdown("---")
    
    # Advanced Charts Section
    st.markdown("### 📊 Advanced Analytics")
    
    # Create tabs for different analytics views
    tab1, tab2, tab3, tab4 = st.tabs(["Risk Analysis", "Transaction Patterns", "Network Analysis", "Performance Metrics"])
    
    with tab1:
        # Risk Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk score distribution
            st.subheader("Risk Score Distribution")
            
            if st.session_state.transactions:
                risk_scores = [t['ml_score'] * 100 for t in st.session_state.transactions]
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=risk_scores,
                    nbinsx=20,
                    name='Risk Score Distribution',
                    marker_color='#0052FF',
                    opacity=0.8
                ))
                
                fig.update_layout(
                    xaxis_title="Risk Score (%)",
                    yaxis_title="Number of Transactions",
                    template=chart_theme,
                    height=400,
                    showlegend=False
                )
                
                # Add average line
                avg_risk = np.mean(risk_scores)
                fig.add_vline(x=avg_risk, line_dash="dash", line_color="red",
                            annotation_text=f"Avg: {avg_risk:.1f}%")
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Risk level breakdown
            st.subheader("Risk Level Breakdown")
            
            risk_counts = pd.DataFrame([
                {'Risk Level': level, 'Count': len([t for t in st.session_state.transactions if t['risk_level'] == level])}
                for level in ['Critical', 'High', 'Medium', 'Low']
            ])
            
            fig = px.pie(
                risk_counts,
                values='Count',
                names='Risk Level',
                color_discrete_map={
                    'Critical': '#FF5252',
                    'High': '#FF9800',
                    'Medium': '#FFC107',
                    'Low': '#00D395'
                },
                hole=0.4
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                template=chart_theme,
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Risk trends over time
        st.subheader("Risk Trends Over Time")
        
        if st.session_state.transactions:
            df_risk = pd.DataFrame(st.session_state.transactions)
            df_risk['hour'] = pd.to_datetime(df_risk['timestamp']).dt.floor('H')
            
            # Calculate hourly risk metrics
            hourly_risk = df_risk.groupby('hour').agg({
                'ml_score': ['mean', 'max', 'min'],
                'hash': 'count'
            }).reset_index()
            
            hourly_risk.columns = ['hour', 'avg_risk', 'max_risk', 'min_risk', 'count']
            
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                subplot_titles=('Average Risk Score', 'Transaction Count'),
                vertical_spacing=0.1
            )
            
            # Risk score trend
            fig.add_trace(
                go.Scatter(
                    x=hourly_risk['hour'],
                    y=hourly_risk['avg_risk'] * 100,
                    mode='lines+markers',
                    name='Avg Risk',
                    line=dict(color='#0052FF', width=3),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )
            
            # Add confidence band
            fig.add_trace(
                go.Scatter(
                    x=hourly_risk['hour'],
                    y=hourly_risk['max_risk'] * 100,
                    mode='lines',
                    name='Max Risk',
                    line=dict(color='rgba(255, 82, 82, 0.3)'),
                    showlegend=False
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=hourly_risk['hour'],
                    y=hourly_risk['min_risk'] * 100,
                    mode='lines',
                    name='Min Risk',
                    line=dict(color='rgba(0, 211, 149, 0.3)'),
                    fill='tonexty',
                    showlegend=False
                ),
                row=1, col=1
            )
            
            # Transaction count
            fig.add_trace(
                go.Bar(
                    x=hourly_risk['hour'],
                    y=hourly_risk['count'],
                    name='Transaction Count',
                    marker_color='#00D395'
                ),
                row=2, col=1
            )
            
            fig.update_xaxes(title_text="Time", row=2, col=1)
            fig.update_yaxes(title_text="Risk Score (%)", row=1, col=1)
            fig.update_yaxes(title_text="Count", row=2, col=1)
            
            fig.update_layout(
                template=chart_theme,
                height=600,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Transaction Patterns
        st.subheader("Transaction Pattern Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Transaction size distribution
            st.markdown("#### Transaction Size Distribution")
            
            if st.session_state.transactions:
                tx_sizes = [t['total_value_btc'] for t in st.session_state.transactions]
                
                fig = px.box(
                    y=tx_sizes,
                    title="Transaction Size Distribution (BTC)",
                    points="all"
                )
                
                fig.update_traces(marker_color='#0052FF')
                fig.update_layout(
                    template=chart_theme,
                    height=400,
                    yaxis_title="Transaction Size (BTC)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Input/Output analysis
            st.markdown("#### Input/Output Analysis")
            
            if st.session_state.transactions:
                df_io = pd.DataFrame(st.session_state.transactions)
                
                fig = px.scatter(
                    df_io,
                    x='num_inputs',
                    y='num_outputs',
                    color='risk_level',
                    size='total_value_btc',
                    color_discrete_map={
                        'Critical': '#FF5252',
                        'High': '#FF9800',
                        'Medium': '#FFC107',
                        'Low': '#00D395'
                    },
                    title="Inputs vs Outputs by Risk Level",
                    hover_data=['hash', 'ml_score']
                )
                
                fig.update_layout(
                    template=chart_theme,
                    height=400,
                    xaxis_title="Number of Inputs",
                    yaxis_title="Number of Outputs"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Smurfing pattern analysis
        st.markdown("#### Smurfing Pattern Detection")
        
        smurfing_tx = [t for t in st.session_state.transactions if t['is_smurfing_rule']]
        
        if smurfing_tx:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Smurfing Transactions", len(smurfing_tx))
            
            with col2:
                smurfing_rate = (len(smurfing_tx) / len(st.session_state.transactions)) * 100
                st.metric("Smurfing Rate", f"{smurfing_rate:.1f}%")
            
            with col3:
                avg_outputs = np.mean([t['num_outputs'] for t in smurfing_tx])
                st.metric("Avg Outputs (Smurfing)", f"{avg_outputs:.0f}")
            
            # Smurfing characteristics
            df_smurfing = pd.DataFrame(smurfing_tx)
            
            fig = px.histogram(
                df_smurfing,
                x='num_outputs',
                title="Output Distribution in Smurfing Transactions",
                nbins=30
            )
            
            fig.update_traces(marker_color='#FF5252')
            fig.update_layout(
                template=chart_theme,
                xaxis_title="Number of Outputs",
                yaxis_title="Count"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No smurfing patterns detected in the current dataset")
    
    with tab3:
        # Network Analysis
        st.subheader("Network Analysis")
        
        # Placeholder for graph-based analytics
        st.info("Network analysis would show transaction flow patterns and address clustering")
        
        # Mock network statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Connected Components", "127", help="Number of separate transaction clusters")
        
        with col2:
            st.metric("Average Degree", "3.4", help="Average connections per address")
        
        with col3:
            st.metric("Network Density", "0.023", help="Overall network connectivity")
        
        # Address reuse analysis
        st.markdown("#### Address Reuse Analysis")
        
        # This would be calculated from actual blockchain data
        reuse_data = pd.DataFrame({
            'Address Type': ['Single Use', 'Low Reuse (2-5)', 'Medium Reuse (6-20)', 'High Reuse (>20)'],
            'Count': [450, 230, 120, 45]
        })
        
        fig = px.bar(
            reuse_data,
            x='Address Type',
            y='Count',
            title="Address Reuse Patterns",
            color='Count',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            template=chart_theme,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Performance Metrics
        st.subheader("System Performance Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Detection performance
            st.markdown("#### Detection Performance")
            
            # Mock performance data
            performance_data = pd.DataFrame({
                'Metric': ['True Positive Rate', 'False Positive Rate', 'Precision', 'Recall', 'F1 Score'],
                'Value': [0.94, 0.06, 0.91, 0.94, 0.925]
            })
            
            fig = px.bar(
                performance_data,
                x='Metric',
                y='Value',
                title="ML Model Performance",
                text='Value'
            )
            
            fig.update_traces(
                marker_color='#0052FF',
                texttemplate='%{text:.2%}',
                textposition='outside'
            )
            
            fig.update_layout(
                template=chart_theme,
                yaxis_range=[0, 1.1],
                yaxis_tickformat='.0%'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Processing speed
            st.markdown("#### Processing Speed")
            
            # Mock speed data
            speed_data = pd.DataFrame({
                'Hour': pd.date_range(start='today', periods=24, freq='H'),
                'Transactions/sec': np.random.normal(150, 20, 24)
            })
            
            fig = px.line(
                speed_data,
                x='Hour',
                y='Transactions/sec',
                title="Transaction Processing Speed (24h)",
                markers=True
            )
            
            fig.update_traces(line_color='#00D395')
            fig.update_layout(
                template=chart_theme,
                yaxis_title="Transactions per Second"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Alert efficiency
        st.markdown("#### Alert Efficiency")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Alerts Generated", len(st.session_state.alerts))
        
        with col2:
            resolved = len([a for a in st.session_state.alerts if a['status'] == 'Resolved'])
            st.metric("Alerts Resolved", resolved)
        
        with col3:
            if st.session_state.alerts:
                resolution_rate = (resolved / len(st.session_state.alerts)) * 100
                st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
            else:
                st.metric("Resolution Rate", "N/A")
        
        with col4:
            st.metric("Avg Response Time", "15 min", help="Average time to first investigation")
    
    # Export options
    st.markdown("---")
    st.markdown("### 📥 Export Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Charts as PDF"):
            st.info("PDF export functionality would be implemented here")
    
    with col2:
        if st.button("📋 Export Data as Excel"):
            st.info("Excel export functionality would be implemented here")
    
    with col3:
        if st.button("📈 Generate Report"):
            st.info("Automated report generation would be implemented here")