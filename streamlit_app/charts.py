# Chart creation utilities for Streamlit app

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from data_generator import (
    generate_hourly_data, 
    generate_weekly_data, 
    generate_monthly_data,
    generate_risk_distribution,
    generate_geographic_data,
    generate_time_series_data
)

def create_hourly_volume_chart():
    """Create hourly transaction volume chart"""
    data = generate_hourly_data()
    
    fig = px.line(
        x=data['hours'], 
        y=data['transaction_counts'],
        title="Hourly Transaction Volume (24h)",
        labels={'x': 'Hour', 'y': 'Transactions'}
    )
    
    fig.update_traces(
        line=dict(color='#0052ff', width=3),
        mode='lines+markers',
        marker=dict(size=6)
    )
    
    fig.update_layout(
        xaxis_title="Hour",
        yaxis_title="Transactions",
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif")
    )
    
    return fig

def create_risk_distribution_pie():
    """Create risk level distribution pie chart"""
    data = generate_risk_distribution()
    
    fig = px.pie(
        values=data['counts'], 
        names=data['risk_levels'],
        title="Risk Level Distribution",
        color_discrete_sequence=data['colors']
    )
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        height=400,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5),
        font=dict(family="Inter, sans-serif")
    )
    
    return fig

def create_risk_trend_chart():
    """Create risk score trend chart"""
    data = generate_hourly_data()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['hours'],
        y=data['risk_scores'],
        mode='lines+markers',
        name='Risk Score',
        line=dict(color='#ea580c', width=3),
        marker=dict(size=8, color='#ea580c'),
        fill='tonexty',
        fillcolor='rgba(234, 88, 12, 0.1)'
    ))
    
    fig.update_layout(
        title='Risk Score Trend (24h)',
        xaxis_title='Time',
        yaxis_title='Risk Score (%)',
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif")
    )
    
    return fig

def create_alert_volume_chart():
    """Create alert volume bar chart"""
    data = generate_hourly_data()
    
    fig = px.bar(
        x=data['hours'],
        y=data['alert_counts'],
        title='Alert Volume (24h)',
        labels={'x': 'Hour', 'y': 'Alerts'}
    )
    
    fig.update_traces(marker_color='#dc2626')
    
    fig.update_layout(
        xaxis_title="Hour",
        yaxis_title="Alert Count",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif")
    )
    
    return fig

def create_weekly_trends_chart():
    """Create weekly risk trends chart"""
    data = generate_weekly_data()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['weeks'],
        y=data['high_risk'],
        mode='lines+markers',
        name='High Risk',
        line=dict(color='#dc2626', width=2),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=data['weeks'],
        y=data['medium_risk'],
        mode='lines+markers',
        name='Medium Risk',
        line=dict(color='#ea580c', width=2),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=data['weeks'],
        y=data['low_risk'],
        mode='lines+markers',
        name='Low Risk',
        line=dict(color='#059669', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title='Weekly Risk Trends',
        xaxis_title='Week',
        yaxis_title='Transaction Count',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif")
    )
    
    return fig

def create_detection_accuracy_chart():
    """Create monthly detection accuracy chart"""
    data = generate_monthly_data()
    
    fig = px.bar(
        x=data['months'], 
        y=data['detection_rate'],
        title="Monthly Fraud Detection Accuracy",
        labels={'x': 'Month', 'y': 'Detection Rate (%)'}
    )
    
    fig.update_traces(marker_color='#0052ff')
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Detection Rate (%)",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif")
    )
    
    return fig

def create_volume_vs_risk_scatter():
    """Create transaction volume vs risk score scatter plot"""
    # Generate sample data
    data = []
    for i in range(100):
        import random
        volume = random.uniform(0.1, 50.0)
        # Higher volumes tend to have slightly higher risk scores
        risk_base = random.uniform(20, 80)
        risk_modifier = min(volume / 10, 20)  # Cap the modifier
        risk_score = min(risk_base + risk_modifier, 100)
        
        data.append({
            'volume': volume,
            'risk_score': risk_score,
            'size': random.randint(1, 10)  # For bubble size
        })
    
    df = pd.DataFrame(data)
    
    fig = px.scatter(
        df,
        x='volume',
        y='risk_score',
        size='size',
        title='Transaction Volume vs Risk Score',
        labels={'volume': 'Volume (BTC)', 'risk_score': 'Risk Score (%)'},
        color='risk_score',
        color_continuous_scale=['#059669', '#ea580c', '#dc2626']
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif")
    )
    
    return fig

def create_geographic_distribution_chart():
    """Create geographic transaction distribution chart"""
    geo_data = generate_geographic_data()
    
    fig = px.bar(
        geo_data.head(8),  # Top 8 countries
        x='country',
        y='transaction_count',
        title='Transaction Distribution by Country',
        labels={'country': 'Country', 'transaction_count': 'Transactions'}
    )
    
    fig.update_traces(marker_color='#0052ff')
    
    fig.update_layout(
        xaxis_title="Country",
        yaxis_title="Transaction Count",
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        xaxis_tickangle=-45
    )
    
    return fig

def create_time_series_chart(days=30):
    """Create time series chart showing trends over time"""
    data = generate_time_series_data(days)
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Daily Transactions', 'Daily Risk Score'),
        vertical_spacing=0.12
    )
    
    # Transactions subplot
    fig.add_trace(
        go.Scatter(
            x=data['date'],
            y=data['transactions'],
            mode='lines',
            name='Transactions',
            line=dict(color='#0052ff', width=2)
        ),
        row=1, col=1
    )
    
    # Risk score subplot
    fig.add_trace(
        go.Scatter(
            x=data['date'],
            y=data['risk_score'],
            mode='lines',
            name='Risk Score',
            line=dict(color='#ea580c', width=2)
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title=f'Trends Over Last {days} Days',
        height=500,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif")
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Transactions", row=1, col=1)
    fig.update_yaxes(title_text="Risk Score (%)", row=2, col=1)
    
    return fig

def create_alert_type_distribution():
    """Create alert type distribution chart"""
    from data_generator import generate_alert_data
    alert_data = generate_alert_data(50)
    
    type_counts = alert_data['Type'].value_counts()
    
    fig = px.bar(
        x=type_counts.values,
        y=type_counts.index,
        orientation='h',
        title='Alert Distribution by Type',
        labels={'x': 'Count', 'y': 'Alert Type'}
    )
    
    fig.update_traces(marker_color='#dc2626')
    
    fig.update_layout(
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif")
    )
    
    return fig

def create_heatmap_chart():
    """Create a heatmap showing risk patterns"""
    import numpy as np
    
    # Generate hour vs day of week heatmap data
    hours = list(range(24))
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Generate risk scores for each hour/day combination
    risk_data = []
    for day in days:
        day_risks = []
        for hour in hours:
            # Simulate higher risk during business hours and weekends
            base_risk = 30
            if day in ['Sat', 'Sun']:
                base_risk += 15
            if 9 <= hour <= 17:
                base_risk += 10
            day_risks.append(base_risk + np.random.normal(0, 10))
        risk_data.append(day_risks)
    
    fig = go.Figure(data=go.Heatmap(
        z=risk_data,
        x=hours,
        y=days,
        colorscale='RdYlBu_r',
        showscale=True,
        colorbar=dict(title="Risk Score")
    ))
    
    fig.update_layout(
        title='Risk Score Heatmap (Hour vs Day)',
        xaxis_title='Hour of Day',
        yaxis_title='Day of Week',
        height=400,
        font=dict(family="Inter, sans-serif")
    )
    
    return fig