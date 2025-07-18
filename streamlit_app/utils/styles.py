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
        
        /* Hide default pages section and app text - More aggressive approach */
        [data-testid="stSidebarNav"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            overflow: hidden !important;
        }
        
        /* Hide the entire navigation list */
        [data-testid="stSidebarNav"] > ul {
            display: none !important;
        }
        
        /* Hide navigation expander */
        [data-testid="stSidebarNav"] > div {
            display: none !important;
        }
        
        /* Hide pages navigation container */
        section[data-testid="stSidebarNav"] {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Hide the app pages list items */
        [data-testid="stSidebarNavItems"] {
            display: none !important;
        }
        
        /* Hide navigation links */
        [data-testid="stSidebarNavLink"] {
            display: none !important;
        }
        
        /* Remove space allocated for navigation */
        [data-testid="stSidebar"] > div:first-child > div:first-child {
            display: none !important;
            height: 0 !important;
        }
        
        /* Ensure sidebar content starts at top */
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
            padding-top: 0 !important;
        }
        
        /* Hide any element containing just "app" text */
        [data-testid="stSidebar"] *:contains("app"):not(:has(*)) {
            display: none !important;
        }
        
        /* Remove extra padding from sidebar */
        .css-1d391kg {
            padding-top: 0rem !important;
        }
        
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0rem !important;
        }
        
        /* Force sidebar content to start at top */
        [data-testid="stSidebar"] > div {
            padding-top: 0 !important;
        }
        
        [data-testid="stSidebar"] .element-container:first-child {
            margin-top: 0 !important;
        }
        
        /* Hide the pages section completely */
        section[data-testid="stSidebarNav"] {
            display: none !important;
        }
        
        /* Additional selector to ensure pages are hidden */
        .css-1d391kg > div:first-child {
            display: none !important;
        }
        
        /* Logo styling */
        [data-testid="stSidebar"] [data-testid="stImage"] {
            text-align: center;
            display: flex;
            justify-content: center;
            margin: 0 auto;
        }
        
        [data-testid="stSidebar"] [data-testid="stImage"] img {
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 82, 255, 0.1);
        }
        
        /* Main container */
        .main {
            padding-top: 2rem;
        }
        
        /* Responsive layout adjustments */
        @media (max-width: 1024px) {
            /* Tablet view */
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            /* Adjust columns for better tablet layout */
            [data-testid="column"] {
                margin-bottom: 1rem;
            }
            
            /* Make buttons more touch-friendly */
            .stButton > button {
                min-height: 44px;
                padding: 12px 20px;
                font-size: 15px;
            }
            
            /* Adjust KPI cards */
            .kpi-card {
                height: auto;
                min-height: 120px;
                padding: 20px;
            }
            
            .kpi-value {
                font-size: 28px;
            }
        }
        
        @media (max-width: 768px) {
            /* Mobile view */
            .block-container {
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }
            
            /* Stack columns on mobile */
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                margin-bottom: 1rem;
            }
            
            /* Mobile-friendly buttons */
            .stButton > button {
                width: 100%;
                min-height: 48px;
                font-size: 16px;
            }
            
            /* Adjust KPI cards for mobile */
            .kpi-card {
                padding: 16px;
            }
            
            .kpi-value {
                font-size: 24px;
            }
            
            .kpi-label {
                font-size: 13px;
            }
            
            /* Make text areas responsive */
            .stTextArea textarea {
                font-size: 14px;
            }
            
            /* Adjust chart containers */
            .chart-container {
                padding: 16px;
            }
            
            /* Make transaction cards more compact */
            .transaction-card {
                padding: 16px;
            }
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
            flex-wrap: wrap;
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
        
        /* Chart containers - Enhanced with white background and borders */
        .chart-container {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            border: 1px solid #e5e7eb;
            margin-bottom: 1rem;
        }
        
        /* Ensure plotly charts have white background */
        .js-plotly-plot .plotly {
            background: white !important;
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
            word-break: break-all;
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
            white-space: nowrap;
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
            white-space: nowrap;
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
        
        /* Expander styling for better mobile view */
        .streamlit-expanderHeader {
            font-size: 16px;
            font-weight: 600;
        }
        
        @media (max-width: 768px) {
            .streamlit-expanderHeader {
                font-size: 14px;
            }
        }
        
        /* Text area responsive styling */
        .stTextArea > div > div > textarea {
            font-size: 14px;
            line-height: 1.5;
        }
        
        /* Ensure select boxes are responsive */
        .stSelectbox > div > div {
            min-width: 0;
        }
        
        /* Download button styling */
        .stDownloadButton > button {
            background: #00D395;
            color: white;
        }
        
        .stDownloadButton > button:hover {
            background: #00B880;
        }
    </style>
    """, unsafe_allow_html=True)