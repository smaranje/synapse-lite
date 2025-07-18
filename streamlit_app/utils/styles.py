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
        
        /* CSS Variables for theming */
        :root {
            /* Light mode colors */
            --bg-primary: #ffffff;
            --bg-secondary: #fafbfc;
            --bg-card: #ffffff;
            --text-primary: #050f19;
            --text-secondary: #5e6278;
            --text-tertiary: #6b7280;
            --border-color: #e5e7eb;
            --border-light: #f0f2f5;
            --primary-color: #0052FF;
            --primary-hover: #0041d0;
            --success-color: #00D395;
            --success-hover: #00B880;
            --danger-color: #FF5252;
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.04);
            --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);
            --shadow-primary: 0 4px 12px rgba(0, 82, 255, 0.15);
            --shadow-primary-hover: 0 8px 24px rgba(0, 82, 255, 0.25);
        }
        
        /* Dark mode colors */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-primary: #0a0a0a;
                --bg-secondary: #1a1a1a;
                --bg-card: #1f1f1f;
                --text-primary: #ffffff;
                --text-secondary: #a1a1aa;
                --text-tertiary: #71717a;
                --border-color: #27272a;
                --border-light: #2a2a2a;
                --primary-color: #3b82f6;
                --primary-hover: #2563eb;
                --success-color: #10b981;
                --success-hover: #059669;
                --danger-color: #ef4444;
                --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
                --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.5);
                --shadow-primary: 0 4px 12px rgba(59, 130, 246, 0.3);
                --shadow-primary-hover: 0 8px 24px rgba(59, 130, 246, 0.4);
            }
            
            /* Dark mode specific adjustments */
            .stApp {
                background-color: var(--bg-primary);
            }
            
            /* Ensure plotly charts adapt to dark mode */
            .js-plotly-plot .plotly {
                background: var(--bg-card) !important;
            }
            
            .js-plotly-plot .plotly .bg {
                fill: var(--bg-card) !important;
            }
            
            /* Dark mode for plotly text */
            .js-plotly-plot .plotly text {
                fill: var(--text-secondary) !important;
            }
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
            box-shadow: var(--shadow-primary);
        }
        
        /* Main container */
        .main {
            padding-top: 2rem;
            background-color: var(--bg-primary);
        }
        
        /* Mobile-first responsive design */
        /* Base mobile styles */
        .block-container {
            padding: 1rem;
            max-width: 100%;
        }
        
        /* Ensure columns stack on mobile */
        @media (max-width: 768px) {
            /* Force single column layout on mobile */
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                max-width: 100% !important;
                margin-bottom: 1rem;
            }
            
            /* Override Streamlit's column behavior */
            .row-widget.stHorizontal {
                flex-direction: column !important;
                gap: 1rem;
            }
            
            /* Ensure proper spacing between stacked columns */
            .row-widget.stHorizontal > [data-testid="column"] {
                min-width: 100% !important;
            }
        }
        
        /* Tablet styles */
        @media (min-width: 769px) and (max-width: 1024px) {
            .block-container {
                padding: 1.5rem;
            }
            
            /* Two-column layout on tablets for 4-column sections */
            [data-testid="column"]:nth-child(odd) {
                margin-right: 1rem;
            }
        }
        
        /* Desktop styles */
        @media (min-width: 1025px) {
            .block-container {
                padding: 2rem;
                max-width: 1400px;
            }
        }

        /* KPI Cards - Responsive with dark mode support */
        .kpi-card {
            background: var(--primary-color);
            color: white;
            padding: 16px;
            border-radius: 12px;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: var(--shadow-primary);
            transition: all 0.3s ease;
            margin-bottom: 1rem;
        }
        
        @media (min-width: 769px) {
            .kpi-card {
                padding: 20px;
                border-radius: 16px;
                height: 140px;
                margin-bottom: 0;
            }
        }
        
        @media (min-width: 1025px) {
            .kpi-card {
                padding: 24px;
            }
        }
        
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-primary-hover);
        }
        
        .kpi-label {
            font-size: 13px;
            font-weight: 500;
            opacity: 0.9;
            margin-bottom: 4px;
        }
        
        @media (min-width: 769px) {
            .kpi-label {
                font-size: 14px;
                margin-bottom: 8px;
            }
        }
        
        .kpi-value {
            font-size: 24px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 4px;
        }
        
        @media (min-width: 769px) {
            .kpi-value {
                font-size: 28px;
                margin-bottom: 8px;
            }
        }
        
        @media (min-width: 1025px) {
            .kpi-value {
                font-size: 32px;
            }
        }
        
        .kpi-delta {
            font-size: 12px;
            font-weight: 500;
            opacity: 0.85;
        }
        
        @media (min-width: 769px) {
            .kpi-delta {
                font-size: 13px;
            }
        }
        
        .kpi-delta.positive::before {
            content: "↑ ";
        }
        
        /* Status indicators - Clean version with dark mode support */
        .status-indicator-clean {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: var(--text-secondary);
            font-weight: 500;
            flex-wrap: wrap;
            margin-bottom: 0.5rem;
        }
        
        @media (min-width: 769px) {
            .status-indicator-clean {
                font-size: 14px;
                gap: 8px;
                margin-bottom: 0;
            }
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--success-color);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(0.95); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        /* Chart containers - Enhanced with dark mode support */
        .chart-container {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 16px;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-color);
            margin-bottom: 1rem;
        }
        
        @media (min-width: 769px) {
            .chart-container {
                border-radius: 16px;
                padding: 20px;
            }
        }
        
        @media (min-width: 1025px) {
            .chart-container {
                padding: 24px;
            }
        }
        
        /* Transaction cards - Clean design with dark mode */
        .transaction-card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
            border: 1px solid var(--border-light);
            transition: all 0.2s ease;
        }
        
        @media (min-width: 769px) {
            .transaction-card {
                padding: 20px;
            }
        }
        
        .transaction-card:hover {
            border-color: var(--border-color);
            box-shadow: var(--shadow-md);
        }
        
        .tx-hash {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 4px;
            word-break: break-all;
        }
        
        @media (min-width: 769px) {
            .tx-hash {
                font-size: 14px;
            }
        }
        
        .tx-details {
            font-size: 12px;
            color: var(--text-tertiary);
            line-height: 1.5;
        }
        
        @media (min-width: 769px) {
            .tx-details {
                font-size: 13px;
            }
        }
        
        /* Risk badges - Clean version */
        .risk-badge-clean {
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            color: white;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
            display: inline-block;
        }
        
        @media (min-width: 769px) {
            .risk-badge-clean {
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 12px;
            }
        }
        
        /* Button styling - Responsive with dark mode */
        .stButton > button {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.2s ease;
            box-shadow: var(--shadow-sm);
            white-space: nowrap;
            width: 100%;
            min-height: 44px;
        }
        
        @media (min-width: 769px) {
            .stButton > button {
                padding: 12px 24px;
                border-radius: 12px;
                width: auto;
            }
        }
        
        .stButton > button:hover {
            background: var(--primary-hover);
            box-shadow: var(--shadow-primary);
            transform: translateY(-1px);
        }
        
        /* Sidebar styling with dark mode */
        .css-1d391kg {
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
        }
        
        [data-testid="stSidebar"] {
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
        }
        
        /* Headers with dark mode support */
        h1 {
            color: var(--text-primary);
            font-weight: 700;
            font-size: 24px;
            margin-bottom: 16px;
        }
        
        @media (min-width: 769px) {
            h1 {
                font-size: 28px;
                margin-bottom: 20px;
            }
        }
        
        @media (min-width: 1025px) {
            h1 {
                font-size: 32px;
                margin-bottom: 24px;
            }
        }
        
        h2 {
            color: var(--text-primary);
            font-weight: 600;
            font-size: 18px;
            margin-bottom: 12px;
        }
        
        @media (min-width: 769px) {
            h2 {
                font-size: 20px;
                margin-bottom: 16px;
            }
        }
        
        h3 {
            color: var(--text-primary);
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 12px;
        }
        
        @media (min-width: 769px) {
            h3 {
                font-size: 18px;
                margin-bottom: 16px;
            }
        }
        
        /* Metric containers override */
        [data-testid="metric-container"] {
            background: transparent;
            border: none;
            padding: 0;
            box-shadow: none;
        }
        
        /* Radio button styling with dark mode */
        .stRadio > div {
            gap: 8px;
            flex-wrap: wrap;
        }
        
        @media (min-width: 769px) {
            .stRadio > div {
                gap: 12px;
            }
        }
        
        .stRadio > div > label {
            font-weight: 500;
            color: var(--text-secondary);
            transition: all 0.2s ease;
            font-size: 14px;
        }
        
        .stRadio > div > label:hover {
            color: var(--primary-color);
        }
        
        /* Info and success boxes with dark mode */
        .stInfo, .stSuccess {
            background: var(--bg-card);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-size: 14px;
        }
        
        /* Divider with dark mode */
        hr {
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 16px 0;
        }
        
        @media (min-width: 769px) {
            hr {
                margin: 24px 0;
            }
        }
        
        /* Plotly toolbar hide */
        .modebar {
            display: none !important;
        }
        
        /* Expander styling for better mobile view */
        .streamlit-expanderHeader {
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        @media (min-width: 769px) {
            .streamlit-expanderHeader {
                font-size: 16px;
            }
        }
        
        /* Text area responsive styling with dark mode */
        .stTextArea > div > div > textarea {
            font-size: 14px;
            line-height: 1.5;
            background: var(--bg-card);
            color: var(--text-primary);
            border-color: var(--border-color);
        }
        
        /* Ensure select boxes are responsive */
        .stSelectbox > div > div {
            min-width: 0;
            background: var(--bg-card);
            color: var(--text-primary);
        }
        
        /* Download button styling */
        .stDownloadButton > button {
            background: var(--success-color);
            color: white;
        }
        
        .stDownloadButton > button:hover {
            background: var(--success-hover);
        }
        
        /* Fix for Details button and small buttons */
        .row-widget.stButton {
            min-width: 80px;
        }
        
        /* Transaction details button specific */
        [data-testid="column"]:last-child .stButton > button {
            padding: 8px 16px;
            font-size: 13px;
            min-width: 70px;
        }
        
        /* Hash display improvement */
        code {
            background-color: rgba(0, 82, 255, 0.1);
            color: var(--primary-color);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', monospace;
            font-size: 13px;
            font-weight: 500;
        }
        
        /* Fix selectbox dropdown visibility */
        .stSelectbox > div > div > select {
            background: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
        }
        
        /* Ensure dropdown options are visible */
        .stSelectbox option {
            background: var(--bg-card);
            color: var(--text-primary);
            padding: 8px;
        }
        
        /* Chart theme dropdown specific fix */
        [data-testid="stSelectbox"] > div > div {
            background: var(--bg-card) !important;
        }
        
        /* Transaction Details section spacing */
        .element-container:has(.stExpander) {
            margin-top: 8px;
        }
        
        /* Risk badge in column fix */
        [data-testid="column"] .risk-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 60px;
        }
        
        /* Additional mobile-specific fixes */
        @media (max-width: 768px) {
            /* Hide sidebar on mobile by default */
            [data-testid="stSidebar"] {
                transform: translateX(-100%);
            }
            
            [data-testid="stSidebar"][data-open="true"] {
                transform: translateX(0);
            }
            
            /* Adjust main content when sidebar is hidden */
            .main .block-container {
                max-width: 100%;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            /* Make tables scrollable on mobile */
            .stDataFrame {
                overflow-x: auto;
            }
            
            /* Adjust tab container for mobile */
            .stTabs [data-baseweb="tab-list"] {
                gap: 0.5rem;
                overflow-x: auto;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: 0.5rem 1rem;
                font-size: 14px;
            }
        }
        
        /* Ensure proper text color in dark mode */
        @media (prefers-color-scheme: dark) {
            p, span, div {
                color: var(--text-primary);
            }
            
            /* Fix input fields in dark mode */
            input, textarea, select {
                background: var(--bg-card) !important;
                color: var(--text-primary) !important;
                border-color: var(--border-color) !important;
            }
            
            /* Fix dropdown menus in dark mode */
            [data-baseweb="select"] {
                background: var(--bg-card) !important;
            }
            
            [data-baseweb="select"] > div {
                background: var(--bg-card) !important;
                color: var(--text-primary) !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)