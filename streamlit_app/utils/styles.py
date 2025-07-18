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
            
            /* Fix plotly chart backgrounds in dark mode */
            .js-plotly-plot .plotly .main-svg {
                background: transparent !important;
            }
            
            .js-plotly-plot .plotly .svg-container {
                background: transparent !important;
            }
            
            /* Fix plotly paper and plot backgrounds */
            .plotly-graph-div {
                background: transparent !important;
            }
            
            /* Ensure pie chart text is visible */
            .js-plotly-plot .plotly .pie text {
                fill: white !important;
                stroke: rgba(0,0,0,0.5) !important;
                stroke-width: 0.5px !important;
            }
        }
        
        /* Light mode specific fixes */
        @media (prefers-color-scheme: light) {
            /* Fix chart text visibility in light mode */
            .js-plotly-plot .plotly text {
                fill: #050f19 !important;
            }
            
            /* Fix pie chart text in light mode */
            .js-plotly-plot .plotly .pie text {
                fill: #050f19 !important;
                stroke: rgba(255,255,255,0.8) !important;
                stroke-width: 2px !important;
                font-weight: 600 !important;
            }
            
            /* Ensure axis lines are visible */
            .js-plotly-plot .plotly .crisp {
                stroke: #e5e7eb !important;
            }
            
            /* Fix grid lines */
            .js-plotly-plot .plotly .gridlayer line {
                stroke: #f0f2f5 !important;
            }
            
            /* Fix sidebar text visibility in light mode */
            [data-testid="stSidebar"] {
                background: #fafbfc !important;
            }
            
            [data-testid="stSidebar"] .stRadio > div > label {
                color: #050f19 !important;
            }
            
            [data-testid="stSidebar"] h3, 
            [data-testid="stSidebar"] h4 {
                color: #050f19 !important;
            }
            
            /* Fix metric values in sidebar */
            [data-testid="stSidebar"] [data-testid="metric-container"] label {
                color: #5e6278 !important;
            }
            
            [data-testid="stSidebar"] [data-testid="metric-container"] [data-testid="stMetricValue"] {
                color: #050f19 !important;
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

        /* KPI Cards - Coinbase style with dark mode support */
        .kpi-card {
            background: var(--bg-card);
            color: var(--text-primary);
            padding: 20px;
            border-radius: 8px;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border: 1px solid var(--border-color);
            transition: all 0.2s ease;
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
        }
        
        /* Blue accent stripe on left */
        .kpi-card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;
            background: var(--primary-color);
        }
        
        .kpi-card:hover {
            border-color: var(--primary-color);
            transform: translateY(-1px);
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
            font-weight: 400;
            color: var(--text-secondary);
            margin-bottom: 8px;
            letter-spacing: 0.01em;
        }
        
        @media (min-width: 769px) {
            .kpi-label {
                font-size: 14px;
                margin-bottom: 8px;
            }
        }
        
        .kpi-value {
            font-size: 28px;
            font-weight: 600;
            line-height: 1.1;
            margin-bottom: 8px;
            color: var(--text-primary);
            letter-spacing: -0.02em;
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
            font-size: 13px;
            font-weight: 500;
            color: var(--text-secondary);
        }
        
        .kpi-delta.positive {
            color: var(--success-color);
        }
        
        .kpi-delta.negative {
            color: var(--danger-color);
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
        }
        
        /* Chart containers - Coinbase style with dark mode support */
        .chart-container {
            background: var(--bg-card);
            border-radius: 8px;
            padding: 16px;
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
        
        /* Transaction cards - Coinbase style with dark mode */
        .transaction-card {
            background: var(--bg-card);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            border: 1px solid var(--border-color);
            transition: all 0.15s ease;
        }
        
        @media (min-width: 769px) {
            .transaction-card {
                padding: 20px;
            }
        }
        
        .transaction-card:hover {
            border-color: var(--primary-color);
            transform: translateY(-1px);
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
        
        /* Risk badges - Coinbase style */
        .risk-badge-clean {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            text-transform: none;
            letter-spacing: 0;
            white-space: nowrap;
            display: inline-block;
            border: 1px solid transparent;
        }
        
        /* Risk level specific styles */
        .risk-badge-clean[data-risk="Critical"] {
            background: #FEE4E2;
            color: #DC2626;
            border-color: #FECACA;
        }
        
        .risk-badge-clean[data-risk="High"] {
            background: #FEF3C7;
            color: #D97706;
            border-color: #FDE68A;
        }
        
        .risk-badge-clean[data-risk="Medium"] {
            background: #FEF3C7;
            color: #D97706;
            border-color: #FDE68A;
        }
        
        .risk-badge-clean[data-risk="Low"] {
            background: #D4F4DD;
            color: #059669;
            border-color: #A7F3D0;
        }
        
        /* Dark mode risk badges */
        @media (prefers-color-scheme: dark) {
            .risk-badge-clean[data-risk="Critical"] {
                background: rgba(220, 38, 38, 0.2);
                color: #FCA5A5;
                border-color: rgba(220, 38, 38, 0.3);
            }
            
            .risk-badge-clean[data-risk="High"] {
                background: rgba(217, 119, 6, 0.2);
                color: #FCD34D;
                border-color: rgba(217, 119, 6, 0.3);
            }
            
            .risk-badge-clean[data-risk="Medium"] {
                background: rgba(217, 119, 6, 0.2);
                color: #FCD34D;
                border-color: rgba(217, 119, 6, 0.3);
            }
            
            .risk-badge-clean[data-risk="Low"] {
                background: rgba(5, 150, 105, 0.2);
                color: #6EE7B7;
                border-color: rgba(5, 150, 105, 0.3);
            }
        }
        
        @media (min-width: 769px) {
            .risk-badge-clean {
                padding: 6px 12px;
                border-radius: 8px;
                font-size: 12px;
            }
        }
        
        /* Button styling - Coinbase style with dark mode */
        .stButton > button {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.15s ease;
            white-space: nowrap;
            width: 100%;
            min-height: 40px;
            letter-spacing: 0.01em;
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
            transform: translateY(-1px);
        }
        
        /* Secondary button style */
        .stButton > button[kind="secondary"] {
            background: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }
        
        .stButton > button[kind="secondary"]:hover {
            background: var(--bg-secondary);
            border-color: var(--text-secondary);
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
        
        /* Fix selectbox dropdown menu visibility */
        [data-baseweb="popover"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            box-shadow: var(--shadow-md) !important;
        }
        
        [data-baseweb="popover"] [role="listbox"] {
            background: var(--bg-card) !important;
            max-height: 300px !important;
            overflow-y: auto !important;
        }
        
        [data-baseweb="popover"] [role="option"] {
            background: var(--bg-card) !important;
            color: var(--text-primary) !important;
            padding: 8px 12px !important;
        }
        
        [data-baseweb="popover"] [role="option"]:hover {
            background: var(--bg-secondary) !important;
        }
        
        [data-baseweb="popover"] [role="option"][aria-selected="true"] {
            background: var(--primary-color) !important;
            color: white !important;
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