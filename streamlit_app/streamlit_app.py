"""
Synapse-Lite Fraud Detection System
Main Streamlit Application

This modular application provides real-time Bitcoin transaction monitoring
and AI-powered fraud detection capabilities.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Simple Streamlit App",
    page_icon="🎈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🎈 Simple Streamlit Application")
st.markdown("""
Welcome to this simple Streamlit application! This app demonstrates various Streamlit features including:
- Interactive widgets
- Data visualization
- File upload functionality
- Real-time updates
""")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # User input
    user_name = st.text_input("Enter your name:", "User")
    
    # Slider
    num_points = st.slider("Number of data points:", 10, 1000, 100)
    
    # Select box
    chart_type = st.selectbox(
        "Select chart type:",
        ["Line Chart", "Bar Chart", "Scatter Plot"]
    )
    
    # Color picker
    chart_color = st.color_picker("Pick a color for the chart:", "#1f77b4")

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.header("📊 Data Visualization")
    
    # Generate sample data
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=num_points),
        end=datetime.now(),
        periods=num_points
    )
    
    data = pd.DataFrame({
        'Date': dates,
        'Value': np.cumsum(np.random.randn(num_points)) + 100,
        'Volume': np.random.randint(50, 200, size=num_points)
    })
    
    # Display chart based on selection
    if chart_type == "Line Chart":
        fig = px.line(data, x='Date', y='Value', title=f"Sample Data for {user_name}")
        fig.update_traces(line_color=chart_color)
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Bar Chart":
        fig = px.bar(data.tail(30), x='Date', y='Volume', title=f"Volume Data (Last 30 Days)")
        fig.update_traces(marker_color=chart_color)
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Scatter Plot
        fig = px.scatter(data, x='Value', y='Volume', title=f"Value vs Volume Correlation")
        fig.update_traces(marker_color=chart_color)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.header("📈 Statistics")
    
    # Display metrics
    col2_1, col2_2, col2_3 = st.columns(3)
    
    with col2_1:
        st.metric(
            label="Current Value",
            value=f"{data['Value'].iloc[-1]:.2f}",
            delta=f"{data['Value'].iloc[-1] - data['Value'].iloc[-2]:.2f}"
        )
    
    with col2_2:
        st.metric(
            label="Average Volume",
            value=f"{data['Volume'].mean():.0f}",
            delta=f"{(data['Volume'].tail(10).mean() - data['Volume'].mean()):.0f}"
        )
    
    with col2_3:
        st.metric(
            label="Data Points",
            value=num_points
        )
    
    # Data table
    st.subheader("📋 Recent Data")
    st.dataframe(data.tail(10), use_container_width=True)

# File upload section
st.header("📁 File Upload")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success(f"File uploaded successfully! Shape: {df.shape}")
    
    # Display first few rows
    st.subheader("Preview of uploaded data:")
    st.dataframe(df.head(), use_container_width=True)
    
    # Basic statistics
    if st.checkbox("Show statistics"):
        st.subheader("Data Statistics:")
        st.write(df.describe())

# Interactive elements
st.header("🎮 Interactive Elements")

col3, col4 = st.columns(2)

with col3:
    # Text area
    text_input = st.text_area("Enter some text:", height=100)
    if text_input:
        st.info(f"You entered {len(text_input)} characters")
        
    # Buttons
    if st.button("Click me!"):
        st.balloons()
        st.success("Button clicked! 🎉")

with col4:
    # Checkbox
    show_raw_data = st.checkbox("Show raw data")
    if show_raw_data:
        st.subheader("Raw Data:")
        st.json(data.tail(5).to_dict())
    
    # Radio buttons
    option = st.radio(
        "Choose an option:",
        ["Option A", "Option B", "Option C"]
    )
    st.write(f"You selected: {option}")

# Progress bar example
if st.button("Run simulation"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        progress_bar.progress(i + 1)
        status_text.text(f'Progress: {i+1}%')
    
    status_text.text('Simulation complete!')

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
