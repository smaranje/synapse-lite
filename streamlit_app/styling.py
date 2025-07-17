# Styling and design system for Streamlit app - Coinbase Business Theme

import streamlit as st
from config import APP_TITLE, APP_ICON

def apply_custom_css():
    """Apply Coinbase Business dashboard styling with proper theme support"""
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
        }

        /* Base font application */
        .main, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        }

        /* Remove Streamlit branding and menu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}

        /* Sidebar improvements */
        [data-testid="stSidebar"] {
            background-color: var(--background-color) !important;
            border-right: 1px solid var(--secondary-background-color) !important;
        }

        /* Dashboard Header */
        .cb-dashboard-header {
            background: var(--background-color) !important;
            color: var(--text-color) !important;
            padding: 1.5rem 2rem;
            margin: -1rem -1rem 2rem -1rem;
            border-bottom: 1px solid var(--secondary-background-color);
            border-radius: var(--cb-border-radius-lg);
            box-shadow: var(--cb-shadow);
        }
        
        .cb-balance-display {
            font-size: var(--cb-font-size-4xl) !important;
            font-weight: 700 !important;
            color: var(--text-color) !important;
            margin: 0 !important;
            line-height: 1.1 !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        .cb-balance-change {
            font-size: var(--cb-font-size-base) !important;
            color: var(--cb-green) !important;
            font-weight: 500 !important;
            margin-top: 0.25rem !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* Card Styling - Fixed for both themes */
        .cb-card {
            background: var(--secondary-background-color) !important;
            border: 1px solid var(--secondary-background-color) !important;
            border-radius: var(--cb-border-radius-lg) !important;
            padding: 1.5rem !important;
            margin-bottom: 1.5rem !important;
            box-shadow: var(--cb-shadow) !important;
            transition: all 0.2s ease !important;
            color: var(--text-color) !important;
        }
        
        .cb-card:hover {
            box-shadow: var(--cb-shadow-lg) !important;
            transform: translateY(-1px) !important;
        }

        .cb-card-title {
            font-size: var(--cb-font-size-lg) !important;
            font-weight: 600 !important;
            color: var(--text-color) !important;
            margin: 0 0 1rem 0 !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* Metric Cards - Enhanced visibility */
        .cb-metric-card {
            background: var(--secondary-background-color) !important;
            border: 2px solid var(--secondary-background-color) !important;
            border-radius: var(--cb-border-radius) !important;
            padding: 1.25rem !important;
            text-align: left !important;
            height: 100% !important;
            transition: all 0.2s ease !important;
            color: var(--text-color) !important;
            box-shadow: var(--cb-shadow) !important;
        }
        
        .cb-metric-card:hover {
            box-shadow: var(--cb-shadow-lg) !important;
            transform: translateY(-2px) !important;
            border-color: var(--cb-blue) !important;
        }

        .cb-metric-label {
            font-size: var(--cb-font-size-sm) !important;
            color: var(--text-color) !important;
            opacity: 0.8 !important;
            font-weight: 500 !important;
            margin-bottom: 0.5rem !important;
            text-transform: none !important;
            font-family: 'Inter', sans-serif !important;
        }

        .cb-metric-value {
            font-size: var(--cb-font-size-2xl) !important;
            font-weight: 700 !important;
            color: var(--text-color) !important;
            margin-bottom: 0.25rem !important;
            font-family: 'Inter', sans-serif !important;
        }

        .cb-metric-change {
            font-size: var(--cb-font-size-sm) !important;
            font-weight: 500 !important;
            font-family: 'Inter', sans-serif !important;
        }

        .cb-metric-change.positive {
            color: var(--cb-green) !important;
        }

        .cb-metric-change.negative {
            color: var(--cb-red) !important;
        }

        /* Buttons */
        .cb-btn {
            background: var(--cb-blue) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--cb-border-radius) !important;
            padding: 0.75rem 1.5rem !important;
            font-size: var(--cb-font-size-sm) !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            text-decoration: none !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
            font-family: 'Inter', sans-serif !important;
        }

        .cb-btn:hover {
            background: var(--cb-blue-hover) !important;
            transform: translateY(-1px) !important;
            box-shadow: var(--cb-shadow) !important;
        }

        /* Quick Actions */
        .cb-quick-actions {
            background: var(--secondary-background-color) !important;
            border: 1px solid var(--secondary-background-color) !important;
            border-radius: var(--cb-border-radius-lg) !important;
            padding: 1.5rem !important;
            box-shadow: var(--cb-shadow) !important;
        }

        .cb-action-btn {
            display: flex !important;
            align-items: center !important;
            gap: 0.75rem !important;
            padding: 1rem !important;
            border: 1px solid var(--secondary-background-color) !important;
            border-radius: var(--cb-border-radius) !important;
            background: var(--background-color) !important;
            color: var(--text-color) !important;
            text-decoration: none !important;
            transition: all 0.2s ease !important;
            margin-bottom: 0.5rem !important;
            width: 100% !important;
            font-family: 'Inter', sans-serif !important;
        }

        .cb-action-btn:hover {
            background: var(--secondary-background-color) !important;
            border-color: var(--cb-blue) !important;
            color: var(--cb-blue) !important;
            transform: translateX(4px) !important;
        }

        .cb-action-icon {
            width: 20px !important;
            height: 20px !important;
            font-size: 1.2rem !important;
        }

        /* Status indicators */
        .cb-status-indicator {
            display: flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
            color: var(--text-color) !important;
            font-family: 'Inter', sans-serif !important;
        }

        .cb-status-dot {
            width: 8px !important;
            height: 8px !important;
            border-radius: 50% !important;
        }

        .cb-status-dot.online {
            background-color: var(--cb-green) !important;
        }

        .cb-status-dot.warning {
            background-color: var(--cb-orange) !important;
        }

        .cb-status-dot.error {
            background-color: var(--cb-red) !important;
        }

        /* Alert cards */
        .cb-alert-card {
            background: var(--secondary-background-color) !important;
            border-radius: var(--cb-border-radius) !important;
            padding: 1rem !important;
            margin-bottom: 1rem !important;
            border-left: 4px solid var(--cb-blue) !important;
            box-shadow: var(--cb-shadow-sm) !important;
            color: var(--text-color) !important;
        }

        /* Chart containers */
        .cb-chart-container {
            background: var(--secondary-background-color) !important;
            border-radius: var(--cb-border-radius-lg) !important;
            padding: 1.5rem !important;
            margin-bottom: 1.5rem !important;
            box-shadow: var(--cb-shadow) !important;
        }

        /* Override all text to use Inter font */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        }

        /* Fix any remaining text color issues */
        .cb-card *,
        .cb-metric-card *,
        .cb-dashboard-header *,
        .cb-quick-actions *,
        .cb-action-btn * {
            color: inherit !important;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .cb-balance-display {
                font-size: var(--cb-font-size-3xl) !important;
            }
            
            .cb-metric-value {
                font-size: var(--cb-font-size-xl) !important;
            }
            
            .cb-card, .cb-metric-card {
                padding: 1rem !important;
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
        <div style="margin-top: 0.5rem; opacity: 0.8; font-size: var(--cb-font-size-sm);">
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
        <div style="opacity: 0.8; font-size: var(--cb-font-size-sm);">
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