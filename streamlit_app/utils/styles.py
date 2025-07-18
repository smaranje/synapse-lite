"""
Custom CSS styles for the Synapse-Lite Fraud Detection Dashboard
"""

import streamlit as st

def apply_custom_css():
    """Apply custom CSS styling to the Streamlit app"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Metric cards styling */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, #FFFFFF 0%, #E6F0FF 100%);
            border: 1px solid rgba(0, 82, 255, 0.1);
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        [data-testid="metric-container"]:hover {
            box-shadow: 0 4px 16px rgba(0, 82, 255, 0.15);
            transform: translateY(-2px);
        }
        
        /* Button styling */
        .stButton > button {
            background: #0052FF;
            color: white;
            border: none;
            padding: 0.5rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: #0066CC;
            box-shadow: 0 4px 12px rgba(0, 82, 255, 0.3);
        }
        
        /* Alert cards */
        .alert-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid #F3F4F6;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        .alert-card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }
        
        /* Risk level badges */
        .risk-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
            display: inline-block;
        }
        
        .risk-critical {
            background: #FF5252;
            color: white;
        }
        
        .risk-high {
            background: #FF9800;
            color: white;
        }
        
        .risk-medium {
            background: #FFC107;
            color: #1A1A1A;
        }
        
        .risk-low {
            background: #00D395;
            color: white;
        }
        
        /* Status indicators */
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            margin-right: 1rem;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00D395;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        /* Transaction row styling */
        .transaction-row {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            border: 1px solid #F3F4F6;
            transition: all 0.2s ease;
        }
        
        .transaction-row:hover {
            background: #F9FAFB;
            border-color: #E5E7EB;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: #F9FAFB;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #1A1A1A;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)