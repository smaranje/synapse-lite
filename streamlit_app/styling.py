# Styling and design system for Streamlit app

import streamlit as st
from config import APP_TITLE, APP_ICON

# Removed apply_page_config since st.set_page_config is now called at the top of streamlit_app.py

def apply_custom_css():
    """Apply the Coinbase-inspired CSS styling and hide default Streamlit sidebar nav header. Update sidebar and main background colors for Coinbase palette and high contrast. Ensure all text is visible in both light and dark mode."""
    st.markdown("""
        <style>
        :root {
            --card-text-color-light: #1a1a1a;
            --card-text-color-dark: #fff;
            --card-secondary-text-light: #6b7280;
            --card-secondary-text-dark: #b0b8c1;
        }
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        /* Hide the default Streamlit sidebar navigation header */
        [data-testid="stSidebarNav"] {
            display: none;
        }
        /* Sidebar Coinbase blue */
        section[data-testid="stSidebar"] {
            background: #0052ff !important;
            color: #fff !important;
        }
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] h4, section[data-testid="stSidebar"] h5, section[data-testid="stSidebar"] h6, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] span {
            color: #fff !important;
        }
        /* Main content white background */
        .main, .stApp, [data-testid="stAppViewContainer"] {
            background: #fff !important;
            color: #1a1a1a !important;
        }
        /* Headings and section titles in main content */
        h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, .stSubheader {
            color: #1a1a1a !important;
        }
        /* Secondary text, axis labels, and widget labels */
        .stMarkdown, .stText, .stSubheader, .stCaption, .stMetricLabel, .stMetricDelta, .stRadio label, .stSelectbox label, .stSlider label, .stDataFrame, .stTable, .stPlotlyChart, .stPlotlyChart * {
            color: #1a1a1a !important;
        }
        /* High contrast for dark mode */
        @media (prefers-color-scheme: dark) {
            section[data-testid="stSidebar"] {
                background: #003399 !important;
                color: #fff !important;
            }
            .main, .stApp, [data-testid="stAppViewContainer"] {
                background: #181c24 !important;
                color: #fff !important;
            }
            .metric-card, .alert-card, .transaction-card {
                background: #232b3b !important;
                color: #fff !important;
                border-color: #2d3a54 !important;
            }
            h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, .stSubheader {
                color: #fff !important;
            }
            .stMarkdown, .stText, .stSubheader, .stCaption, .stMetricLabel, .stMetricDelta, .stRadio label, .stSelectbox label, .stSlider label, .stDataFrame, .stTable, .stPlotlyChart, .stPlotlyChart * {
                color: #fff !important;
            }
            /* Plotly chart text in dark mode */
            .js-plotly-plot .plotly .main-svg {
                color: #fff !important;
                fill: #fff !important;
            }
        }
        
        .main {
            background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
            color: #1a1a1a;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        }
        
        /* Header styling */
        h1 {
            color: #0a0b0d;
            font-weight: 600;
            font-size: 2.25rem;
            text-align: center;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }
        
        h2, h3 {
            color: #1a1a1a;
            font-weight: 500;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            letter-spacing: -0.01em;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
            border-right: 1px solid #f0f3f7;
        }
        
        /* Main content area */
        .css-1v0mbdj {
            padding: 2rem 1rem;
        }
        
        /* Metric styling */
        .css-1xarl3l, [data-testid="metric-container"] {
            background: white;
            border: 1px solid #f0f3f7;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        }
        
        /* Button styling */
        .stButton > button {
            background: #0052ff;
            color: white;
            border: none;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 0.875rem;
            padding: 0.625rem 1rem;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background: #0046cc;
            transform: translateY(-1px);
        }
        
        /* Input styling */
        .stTextInput > div > div > input, .stSelectbox > div > div > div {
            border-radius: 8px !important;
            border: 1px solid #f0f3f7 !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.875rem !important;
            padding: 0.75rem !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #0052ff !important;
            box-shadow: 0 0 0 2px rgba(0, 82, 255, 0.1) !important;
        }
        
        /* Chart styling */
        .js-plotly-plot .plotly .modebar {
            right: 10px;
        }
        
        /* Custom card styling */
        .metric-card {
            background: white;
            border: 1px solid #f0f3f7;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            font-family: 'Inter', sans-serif;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--card-text-color-light);
            transition: all 0.2s ease;
        }
        .metric-card .metric-title {
            font-size: 0.875rem;
            color: var(--card-secondary-text-light);
            margin-bottom: 0.25rem;
        }
        .metric-card .metric-value {
            font-size: 1.875rem;
            font-weight: 600;
            color: var(--card-text-color-light);
        }
        .metric-card .metric-delta {
            font-size: 0.875rem;
            margin-top: 0.25rem;
            color: var(--card-secondary-text-light);
        }
        /* FORCE DARK MODE CARD STYLES FOR TESTING */
        .metric-card {
            background: #232b3b !important;
            color: #fff !important;
            border-color: #2d3a54 !important;
        }
        .metric-card .metric-title {
            color: #b0b8c1 !important;
        }
        .metric-card .metric-value {
            color: #fff !important;
        }
        .metric-card .metric-delta {
            color: #b0b8c1 !important;
        }
        /* END FORCE DARK MODE CARD STYLES */
        
        .metric-card:hover {
            border-color: #0052ff;
            background: #f8faff;
        }
        
        /* Alert cards */
        .alert-card {
            background: white;
            border: 1px solid #f0f3f7;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease;
        }
        
        .alert-card:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .alert-card.critical {
            border-left: 4px solid #dc2626;
        }
        
        .alert-card.high {
            border-left: 4px solid #ea580c;
        }
        
        .alert-card.medium {
            border-left: 4px solid #0052ff;
        }
        
        .alert-card.low {
            border-left: 4px solid #059669;
        }
        
        /* Transaction cards */
        .transaction-card {
            background: white;
            border: 1px solid #f0f3f7;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease;
        }
        
        .transaction-card:hover {
            transform: translateY(-1px);
            border-color: #0052ff;
            box-shadow: 0 4px 12px rgba(0, 82, 255, 0.1);
        }
        
        /* Status badges */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .status-badge.confirmed {
            background: #dcfce7;
            color: #166534;
        }
        
        .status-badge.pending {
            background: #fef3c7;
            color: #92400e;
        }
        
        .status-badge.flagged {
            background: #fee2e2;
            color: #991b1b;
        }
        
        /* Risk badges */
        .risk-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .risk-badge.critical {
            background: #dc2626;
            color: white;
        }
        
        .risk-badge.high {
            background: #ea580c;
            color: white;
        }
        
        .risk-badge.medium {
            background: #0052ff;
            color: white;
        }
        
        .risk-badge.low {
            background: #059669;
            color: white;
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            padding: 2rem 0;
            color: #6b7280;
            font-size: 0.875rem;
            border-top: 1px solid #f0f3f7;
            margin-top: 3rem;
        }
        </style>
        """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create a styled metric card"""
    delta_html = ""
    if delta:
        color_class = {
            "normal": "metric-delta",
            "inverse": "metric-delta metric-delta-inverse",
            "off": "metric-delta"
        }
        delta_html = f'<div class="{color_class.get(delta_color, "metric-delta")}">{delta}</div>'
    return f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

def create_status_badge(status):
    """Create a status badge"""
    return f'<span class="status-badge {status.lower()}">{status}</span>'

def create_risk_badge(risk_level):
    """Create a risk level badge"""
    return f'<span class="risk-badge {risk_level.lower()}">{risk_level}</span>'

def apply_styling():
    """Apply all styling configurations"""
    # apply_page_config()  # No longer needed
    apply_custom_css()