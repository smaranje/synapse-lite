# Styling and design system for Streamlit app - Coinbase Business Theme

import streamlit as st
from config import APP_TITLE, APP_ICON

def apply_custom_css():
    """Apply Coinbase Business dashboard styling with clean, modern design"""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            /* Coinbase Brand Colors */
            --cb-blue: #0052ff;
            --cb-blue-hover: #0046e6;
            --cb-blue-light: #1652f0;
            --cb-green: #00d924;
            --cb-red: #f5455c;
            --cb-orange: #ff9500;
            --cb-gray-50: #fafbfc;
            --cb-gray-100: #f4f6f8;
            --cb-gray-200: #e6ebf1;
            --cb-gray-300: #d4dbe3;
            --cb-gray-400: #9aa5b1;
            --cb-gray-500: #708797;
            --cb-gray-600: #5b6975;
            --cb-gray-700: #434d5a;
            --cb-gray-800: #1a1d29;
            --cb-gray-900: #0f1419;
            
            /* Layout */
            --cb-border-radius: 8px;
            --cb-border-radius-lg: 12px;
            --cb-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --cb-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            --cb-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            
            /* Typography */
            --cb-font-size-xs: 0.75rem;
            --cb-font-size-sm: 0.875rem;
            --cb-font-size-base: 1rem;
            --cb-font-size-lg: 1.125rem;
            --cb-font-size-xl: 1.25rem;
            --cb-font-size-2xl: 1.5rem;
            --cb-font-size-3xl: 1.875rem;
            --cb-font-size-4xl: 2.25rem;

            /* Adapt grayscale palette to Streamlit theme so it works in both modes */
            --cb-gray-900: var(--text-color);
            --cb-gray-800: var(--text-color);
            --cb-gray-700: var(--text-color);
            --cb-gray-600: var(--text-color);
            --cb-gray-500: var(--text-color);
            --cb-gray-400: var(--text-color);
            --cb-gray-300: var(--secondary-background-color);
            --cb-gray-200: var(--secondary-background-color);
            --cb-gray-100: var(--secondary-background-color);
            --cb-gray-50: var(--secondary-background-color);
        }

        /* Reset and Base Styles */
        .main > div {
            padding-top: 2rem !important;
        }
        
        /* Let Streamlit handle the actual colours so we are compatible with both light and dark themes */
        .stApp {
            background-color: var(--background-color) !important;
        }

        body, .stApp, .main, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            background-color: var(--background-color) !important;
            color: var(--text-color) !important;
            line-height: 1.5 !important;
        }

        /* Remove Streamlit branding and menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}

        /* Sidebar Styling */
        .css-1d391kg, [data-testid="stSidebar"] {
            background-color: white !important;
            border-right: 1px solid var(--cb-gray-200) !important;
            box-shadow: var(--cb-shadow-sm) !important;
        }
        
        .css-1d391kg .element-container, [data-testid="stSidebar"] .element-container {
            padding: 0 !important;
        }

        /* Custom Header */
        .cb-dashboard-header {
            background: white;
            padding: 1.5rem 2rem;
            margin: -2rem -2rem 2rem -2rem;
            border-bottom: 1px solid var(--cb-gray-200);
            box-shadow: var(--cb-shadow-sm);
        }
        
        .cb-balance-display {
            font-size: var(--cb-font-size-4xl);
            font-weight: 700;
            color: var(--cb-gray-900);
            margin: 0;
            line-height: 1.1;
        }
        
        .cb-balance-change {
            font-size: var(--cb-font-size-base);
            color: var(--cb-green);
            font-weight: 500;
            margin-top: 0.25rem;
        }

        /* Card Styling */
        .cb-card {
            background: white;
            border: 1px solid var(--cb-gray-200);
            border-radius: var(--cb-border-radius-lg);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--cb-shadow-sm);
            transition: all 0.2s ease;
        }
        
        .cb-card:hover {
            box-shadow: var(--cb-shadow);
            border-color: var(--cb-gray-300);
        }

        .cb-card-title {
            font-size: var(--cb-font-size-lg);
            font-weight: 600;
            color: var(--cb-gray-900);
            margin: 0 0 1rem 0;
        }

        /* Metric Cards */
        .cb-metric-card {
            background: white;
            border: 1px solid var(--cb-gray-200);
            border-radius: var(--cb-border-radius);
            padding: 1.25rem;
            text-align: left;
            height: 100%;
            transition: all 0.2s ease;
        }
        
        .cb-metric-card:hover {
            box-shadow: var(--cb-shadow);
        }

        .cb-metric-label {
            font-size: var(--cb-font-size-sm);
            color: var(--cb-gray-600);
            font-weight: 500;
            margin-bottom: 0.5rem;
            text-transform: none;
        }

        .cb-metric-value {
            font-size: var(--cb-font-size-2xl);
            font-weight: 700;
            color: var(--cb-gray-900);
            margin-bottom: 0.25rem;
        }

        .cb-metric-change {
            font-size: var(--cb-font-size-sm);
            font-weight: 500;
        }

        .cb-metric-change.positive {
            color: var(--cb-green);
        }

        .cb-metric-change.negative {
            color: var(--cb-red);
        }

        /* Buttons */
        .cb-btn {
            background: var(--cb-blue);
            color: white;
            border: none;
            border-radius: var(--cb-border-radius);
            padding: 0.75rem 1.5rem;
            font-size: var(--cb-font-size-sm);
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .cb-btn:hover {
            background: var(--cb-blue-hover);
            transform: translateY(-1px);
            box-shadow: var(--cb-shadow);
        }

        .cb-btn-secondary {
            background: white;
            color: var(--cb-blue);
            border: 1px solid var(--cb-gray-200);
        }

        .cb-btn-secondary:hover {
            background: var(--cb-gray-50);
            border-color: var(--cb-blue);
        }

        /* Quick Actions */
        .cb-quick-actions {
            background: white;
            border: 1px solid var(--cb-gray-200);
            border-radius: var(--cb-border-radius-lg);
            padding: 1.5rem;
        }

        .cb-action-btn {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem;
            border: 1px solid var(--cb-gray-200);
            border-radius: var(--cb-border-radius);
            background: white;
            color: var(--cb-gray-900);
            text-decoration: none;
            transition: all 0.2s ease;
            margin-bottom: 0.5rem;
            width: 100%;
        }

        .cb-action-btn:hover {
            background: var(--cb-gray-50);
            border-color: var(--cb-blue);
            color: var(--cb-blue);
        }

        .cb-action-icon {
            width: 20px;
            height: 20px;
            background: var(--cb-blue);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: 600;
        }

        /* Status Indicators */
        .cb-status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: var(--cb-font-size-sm);
            font-weight: 500;
        }

        .cb-status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        .cb-status-dot.online { background: var(--cb-green); }
        .cb-status-dot.warning { background: var(--cb-orange); }
        .cb-status-dot.error { background: var(--cb-red); }

        /* Badges */
        .cb-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: var(--cb-font-size-xs);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Risk badges */
        .cb-badge.critical { 
            background: #fef2f2; 
            color: #dc2626; 
            border: 1px solid #fecaca;
        }
        .cb-badge.high { 
            background: #fff7ed; 
            color: #ea580c; 
            border: 1px solid #fed7aa;
        }
        .cb-badge.medium { 
            background: #fefce8; 
            color: #ca8a04; 
            border: 1px solid #fef08a;
        }
        .cb-badge.low { 
            background: #f0fdf4; 
            color: #16a34a; 
            border: 1px solid #bbf7d0;
        }

        /* Status badges */
        .cb-badge.confirmed { 
            background: #f0fdf4; 
            color: #16a34a; 
            border: 1px solid #bbf7d0;
        }
        .cb-badge.pending { 
            background: #fefce8; 
            color: #ca8a04; 
            border: 1px solid #fef08a;
        }
        .cb-badge.flagged { 
            background: #fef2f2; 
            color: #dc2626; 
            border: 1px solid #fecaca;
        }

        /* Charts */
        .cb-chart-container {
            background: white;
            border: 1px solid var(--cb-gray-200);
            border-radius: var(--cb-border-radius-lg);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }

        /* Tables */
        .cb-table {
            width: 100%;
            background: white;
            border: 1px solid var(--cb-gray-200);
            border-radius: var(--cb-border-radius-lg);
            overflow: hidden;
        }

        .cb-table th {
            background: var(--cb-gray-50);
            padding: 0.75rem 1rem;
            font-size: var(--cb-font-size-sm);
            font-weight: 600;
            color: var(--cb-gray-700);
            border-bottom: 1px solid var(--cb-gray-200);
        }

        .cb-table td {
            padding: 0.75rem 1rem;
            font-size: var(--cb-font-size-sm);
            border-bottom: 1px solid var(--cb-gray-200);
        }

        /* Streamlit overrides */
        .stMetric {
            background: white !important;
            padding: 1.25rem !important;
            border-radius: var(--cb-border-radius) !important;
            border: 1px solid var(--cb-gray-200) !important;
            box-shadow: var(--cb-shadow-sm) !important;
        }

        .stMetric > div {
            color: var(--cb-gray-900) !important;
        }

        .stMetric [data-testid="metric-container"] > div:first-child {
            font-size: var(--cb-font-size-sm) !important;
            color: var(--cb-gray-600) !important;
            font-weight: 500 !important;
        }

        .stMetric [data-testid="metric-container"] > div:nth-child(2) {
            font-size: var(--cb-font-size-2xl) !important;
            font-weight: 700 !important;
            color: var(--cb-gray-900) !important;
        }

        /* Make sure our custom cards pick up the secondary background so text remains visible in both modes */
        .cb-card,
        .cb-metric-card,
        .cb-quick-actions,
        .cb-chart-container,
        .cb-table,
        .cb-dashboard-header,
        .cb-action-btn,
        .cb-btn-secondary {
            background: var(--secondary-background-color) !important;
        }

        /* Universal text colour override for our components */
        .cb-card-title,
        .cb-metric-value,
        .cb-metric-label,
        .cb-balance-display,
        .cb-balance-change,
        .cb-status-indicator,
        [data-testid="stSidebar"] .stRadio > div > label > div {
            color: var(--text-color) !important;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .cb-balance-display {
                font-size: var(--cb-font-size-3xl);
            }
            
            .cb-metric-value {
                font-size: var(--cb-font-size-xl);
            }
        }
        </style>
        """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create a Coinbase-style metric card"""
    delta_class = "positive" if delta_color == "normal" and delta and "+" in str(delta) else "negative" if delta and "-" in str(delta) else "positive"
    
    delta_html = ""
    if delta:
        delta_html = f'<div class="cb-metric-change {delta_class}">{delta}</div>'
    
    return f"""
    <div class="cb-metric-card">
        <div class="cb-metric-label">{title}</div>
        <div class="cb-metric-value">{value}</div>
        {delta_html}
    </div>
    """

def create_status_card(status, description, color="green"):
    """Create a Coinbase-style status card"""
    status_color = "online" if color == "green" else "warning" if color == "yellow" else "error"
    
    return f"""
    <div class="cb-card">
        <div class="cb-status-indicator">
            <div class="cb-status-dot {status_color}"></div>
            <strong>{status}</strong>
        </div>
        <div style="margin-top: 0.5rem; color: var(--cb-gray-600); font-size: var(--cb-font-size-sm);">
            {description}
        </div>
    </div>
    """

def create_alert_card(title, description, level="info"):
    """Create a Coinbase-style alert card"""
    level_colors = {
        "info": "var(--cb-blue)",
        "warning": "var(--cb-orange)", 
        "error": "var(--cb-red)",
        "success": "var(--cb-green)"
    }
    
    color = level_colors.get(level, "var(--cb-blue)")
    
    return f"""
    <div class="cb-card" style="border-left: 4px solid {color};">
        <div class="cb-card-title">{title}</div>
        <div style="color: var(--cb-gray-600); font-size: var(--cb-font-size-sm);">
            {description}
        </div>
    </div>
    """

def create_risk_badge(risk_level):
    """Create a Coinbase-style risk badge"""
    return f'<span class="cb-badge {risk_level.lower()}">{risk_level}</span>'

def create_status_badge(status):
    """Create a Coinbase-style status badge"""
    return f'<span class="cb-badge {status.lower()}">{status}</span>'

def create_dashboard_header(balance, change):
    """Create Coinbase-style dashboard header"""
    return f"""
    <div class="cb-dashboard-header">
        <div class="cb-balance-display">${balance:,.2f}</div>
        <div class="cb-balance-change">↗ {change}</div>
    </div>
    """

def create_quick_actions():
    """Create Coinbase-style quick actions panel"""
    return """
    <div class="cb-quick-actions">
        <div class="cb-card-title">Quick actions</div>
        <a href="#" class="cb-action-btn">
            <div class="cb-action-icon">↑</div>
            <span>Send crypto</span>
        </a>
        <a href="#" class="cb-action-btn">
            <div class="cb-action-icon">↓</div>
            <span>Receive crypto</span>
        </a>
        <a href="#" class="cb-action-btn">
            <div class="cb-action-icon">⇄</div>
            <span>Trade crypto</span>
        </a>
        <a href="#" class="cb-action-btn">
            <div class="cb-action-icon">$</div>
            <span>Deposit cash</span>
        </a>
        <a href="#" class="cb-action-btn">
            <div class="cb-action-icon">←</div>
            <span>Withdraw cash</span>
        </a>
    </div>
    """

def apply_styling():
    """Apply all Coinbase styling configurations"""
    apply_custom_css()