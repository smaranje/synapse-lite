"""Chart creation functions for the fraud detection dashboard."""

import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from .data_generator import generate_analytics_data, generate_dummy_alerts

def create_advanced_charts():
    """Create advanced interactive charts."""
    data = generate_analytics_data()
    
    # Risk Score Trend Chart
    fig_risk = go.Figure()
    fig_risk.add_trace(go.Scatter(
        x=data['hours'],
        y=data['risk_scores'],
        mode='lines+markers',
        name='Risk Score',
        line=dict(color='#4299e1', width=3),
        marker=dict(size=8, color='#63b3ed'),
        fill='tonexty',
        fillcolor='rgba(66, 153, 225, 0.1)'
    ))
    fig_risk.update_layout(
        title='Risk Score Trend (24h)',
        xaxis_title='Time',
        yaxis_title='Risk Score',
        template='plotly_dark',
        height=400,
        showlegend=False
    )
    
    # Transaction Volume Chart
    fig_volume = go.Figure()
    fig_volume.add_trace(go.Bar(
        x=data['hours'],
        y=data['transaction_counts'],
        name='Transactions',
        marker=dict(color='#48bb78', opacity=0.8)
    ))
    fig_volume.update_layout(
        title='Transaction Volume (24h)',
        xaxis_title='Time',
        yaxis_title='Transaction Count',
        template='plotly_dark',
        height=400,
        showlegend=False
    )
    
    # Alert Distribution Pie Chart
    alert_data = generate_dummy_alerts(100)
    risk_counts = alert_data['Risk_Level'].value_counts()
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        hole=0.4,
        marker=dict(colors=['#f56565', '#ed8936', '#4299e1', '#48bb78'])
    )])
    fig_pie.update_layout(
        title='Alert Distribution by Risk Level',
        template='plotly_dark',
        height=400
    )
    
    return fig_risk, fig_volume, fig_pie

def create_ml_score_histogram(transactions):
    """Create ML Score distribution histogram."""
    fig_ml = px.histogram(
        transactions, 
        x='ML_Score', 
        nbins=20, 
        title='ML Score Distribution',
        color_discrete_sequence=['#4299e1']
    )
    fig_ml.update_layout(template='plotly_dark')
    return fig_ml

def create_transaction_scatter(transactions):
    """Create transaction amount vs risk score scatter plot."""
    fig_scatter = px.scatter(
        transactions,
        x='TotalOutputValueBTC',
        y='ML_Score',
        color='Risk_Level',
        size='NumOutputs',
        title='Transaction Amount vs Risk Score',
        color_discrete_map={
            'Critical': '#f56565',
            'High': '#ed8936', 
            'Medium': '#4299e1',
            'Low': '#48bb78'
        }
    )
    fig_scatter.update_layout(template='plotly_dark')
    return fig_scatter