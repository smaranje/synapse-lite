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
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Hide default pages section */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* Remove extra padding from sidebar */
        .css-1d391kg {
            padding-top: 0rem !important;
        }
        
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0rem !important;
        }
        
        /* Hide the pages section completely */
        section[data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* Additional selector to ensure pages are hidden */
        .css-1d391kg > div:first-child {
            display: none !important;
        }
        
        /* Main container */
        .main {
            padding-top: 2rem;
        }
        

        /* Main container */
        .main {
            padding-top: 2rem;
        }
        

        /* Main container */
        .main {
            padding-top: 2rem;
        }
        

        /* KPI Cards - Coinbase style */
        .kpi-card {
            background: #0052FF;
            color: white;
            padding: 24px;
            border-radius: 16px;
            height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 4px 12px rgba(0, 82, 255, 0.15);
            transition: all 0.3s ease;
        }
        
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 82, 255, 0.25);
        }
        
        .kpi-label {
            font-size: 14px;
            font-weight: 500;
            opacity: 0.9;
            margin-bottom: 8px;
        }
        
        .kpi-value {
            font-size: 32px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 8px;
        }
        
        .kpi-delta {
            font-size: 13px;
            font-weight: 500;
            opacity: 0.85;
        }
        
        .kpi-delta.positive::before {
            content: "↑ ";
        }
        
        /* Status indicators - Clean version */
        .status-indicator-clean {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
            color: #5e6278;
            font-weight: 500;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00D395;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(0.95); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        /* Chart containers */
        .chart-container {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            border: 1px solid #f0f2f5;
        }
        
        /* Transaction cards - Clean design */
        .transaction-card {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 12px;
            border: 1px solid #f0f2f5;
            transition: all 0.2s ease;
        }
        
        .transaction-card:hover {
            border-color: #e5e7eb;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        .tx-hash {
            font-size: 14px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 4px;
        }
        
        .tx-details {
            font-size: 13px;
            color: #6b7280;
            line-height: 1.5;
        }
        
        /* Risk badges - Clean version */
        .risk-badge-clean {
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            color: white;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Button styling - Coinbase style */
        .stButton > button {
            background: #0052FF;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0, 82, 255, 0.1);
        }
        
        .stButton > button:hover {
            background: #0041d0;
            box-shadow: 0 4px 12px rgba(0, 82, 255, 0.25);
            transform: translateY(-1px);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: #fafbfc;
            border-right: 1px solid #e5e7eb;
        }
        
        [data-testid="stSidebar"] {
            background: #fafbfc;
            border-right: 1px solid #e5e7eb;
        }
        
        /* Headers */
        h1 {
            color: #050f19;
            font-weight: 700;
            font-size: 32px;
            margin-bottom: 24px;
        }
        
        h2 {
            color: #050f19;
            font-weight: 600;
            font-size: 20px;
            margin-bottom: 16px;
        }
        
        h3 {
            color: #050f19;
            font-weight: 600;
            font-size: 18px;
            margin-bottom: 16px;
        }
        
        /* Metric containers override */
        [data-testid="metric-container"] {
            background: transparent;
            border: none;
            padding: 0;
            box-shadow: none;
        }
        
        /* Radio button styling */
        .stRadio > div {
            gap: 12px;
        }
        
        .stRadio > div > label {
            font-weight: 500;
            color: #5e6278;
            transition: all 0.2s ease;
        }
        
        .stRadio > div > label:hover {
            color: #0052FF;
        }
        
        /* Info and success boxes */
        .stInfo, .stSuccess {
            background: white;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            color: #5e6278;
            font-size: 14px;
        }
        
        /* Divider */
        hr {
            border: none;
            border-top: 1px solid #e5e7eb;
            margin: 24px 0;
        }
        
        /* Plotly toolbar hide */
        .modebar {
            display: none !important;
        }
        
        /* Page padding */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
    </style>
    """, unsafe_allow_html=True)