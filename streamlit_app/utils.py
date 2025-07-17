# Utility functions for Streamlit app

import streamlit as st

def create_status_indicator(status="online", label="System Status"):
    """Create a status indicator with colored circle and label"""
    if status.lower() == "online":
        color = "#10b981"
        text = "Online"
    elif status.lower() == "offline":
        color = "#ef4444"
        text = "Offline"
    elif status.lower() == "warning":
        color = "#f59e0b" 
        text = "Warning"
    else:
        color = "#6b7280"
        text = "Unknown"
    
    return f"""
    <div style="display: flex; align-items: center; gap: 8px; margin: 4px 0;">
        <div style="
            width: 8px; 
            height: 8px; 
            border-radius: 50%; 
            background-color: {color};
        "></div>
        <span style="
            font-size: 0.875rem;
            color: #374151;
            font-weight: 500;
        ">{label}: {text}</span>
    </div>
    """