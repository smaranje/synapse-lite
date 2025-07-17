# Styling and design system for Streamlit app

import streamlit as st
from config import APP_TITLE, APP_ICON

# Removed apply_page_config since st.set_page_config is now called at the top of streamlit_app.py

def apply_custom_css():
    """Apply the Coinbase-inspired CSS styling and hide default Streamlit sidebar nav header. Update sidebar and main background colors for Coinbase palette and high contrast. Ensure all text is visible in both light and dark mode."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        :root {
            --brand-blue: #0052ff;
            --brand-blue-dark: #003399;
            --brand-accent: #0a7cff;
            --brand-bg-light: #f7fafc;
            --brand-bg-dark: #181c24;
            --brand-card-light: #fff;
            --brand-card-dark: #232b3b;
            --brand-shadow: 0 4px 24px rgba(0, 82, 255, 0.08);
            --brand-radius: 16px;
            --brand-text-light: #1a1a1a;
            --brand-text-dark: #fff;
            --brand-secondary-light: #6b7280;
            --brand-secondary-dark: #b0b8c1;
        }
        body, .stApp, .main, [data-testid="stAppViewContainer"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            background: var(--brand-bg-light) !important;
            color: var(--brand-text-light) !important;
        }
        @media (prefers-color-scheme: dark) {
            body, .stApp, .main, [data-testid="stAppViewContainer"] {
                background: var(--brand-bg-dark) !important;
                color: var(--brand-text-dark) !important;
            }
        }
        /* Header */
        .brand-header {
            width: 100%;
            padding: 2rem 0 1rem 0;
            text-align: right;
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--brand-blue);
            letter-spacing: -0.02em;
            background: transparent;
        }
        @media (prefers-color-scheme: dark) {
            .brand-header {
                color: var(--brand-accent);
            }
        }
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background: var(--brand-blue) !important;
            color: #fff !important;
            border-top-right-radius: var(--brand-radius);
            border-bottom-right-radius: var(--brand-radius);
        }
        section[data-testid="stSidebar"] * {
            color: #fff !important;
        }
        [data-testid="stSidebarNav"] { display: none; }
        /* Cards */
        .modern-card {
            background: var(--brand-card-light);
            border-radius: var(--brand-radius);
            box-shadow: var(--brand-shadow);
            padding: 2rem 1.5rem 1.5rem 1.5rem;
            margin: 1rem 0;
            border: none;
            transition: box-shadow 0.2s;
        }
        .modern-card:hover {
            box-shadow: 0 8px 32px rgba(0, 82, 255, 0.16);
        }
        .modern-card .card-title {
            font-size: 1.1rem;
            color: var(--brand-secondary-light);
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        .modern-card .card-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--brand-text-light);
            margin-bottom: 0.25rem;
        }
        .modern-card .card-delta {
            font-size: 1rem;
            color: var(--brand-secondary-light);
        }
        @media (prefers-color-scheme: dark) {
            .modern-card {
                background: var(--brand-card-dark) !important;
                color: var(--brand-text-dark) !important;
            }
            .modern-card .card-title {
                color: var(--brand-secondary-dark) !important;
            }
            .modern-card .card-value {
                color: var(--brand-text-dark) !important;
            }
            .modern-card .card-delta {
                color: var(--brand-secondary-dark) !important;
            }
        }
        /* Status & Alert Cards */
        .status-card {
            background: var(--brand-card-light);
            border-radius: var(--brand-radius);
            box-shadow: var(--brand-shadow);
            padding: 1.5rem 1.25rem;
            margin: 1rem 0;
            border: none;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        @media (prefers-color-scheme: dark) {
            .status-card {
                background: var(--brand-card-dark) !important;
                color: var(--brand-text-dark) !important;
            }
        }
        /* Footer */
        .modern-footer {
            text-align: center;
            padding: 2rem 0 1rem 0;
            color: var(--brand-secondary-light);
            font-size: 1rem;
            border-top: 1px solid #e5e7eb;
            margin-top: 3rem;
        }
        @media (prefers-color-scheme: dark) {
            .modern-footer {
                color: var(--brand-secondary-dark);
                border-top: 1px solid #232b3b;
            }
        }
        /* Badges */
        .risk-badge, .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0 2px;
        }
        /* Risk badges */
        .risk-badge.critical { background: #ef4444; color: white; }
        .risk-badge.high { background: #f97316; color: white; }
        .risk-badge.medium { background: #eab308; color: white; }
        .risk-badge.low { background: #22c55e; color: white; }
        /* Status badges */
        .status-badge.confirmed { background: #22c55e; color: white; }
        .status-badge.pending { background: #eab308; color: white; }
        .status-badge.flagged { background: #ef4444; color: white; }
        /* Responsive */
        @media (max-width: 900px) {
            .brand-header { font-size: 1.5rem; }
            .modern-card .card-value { font-size: 1.5rem; }
        }
        </style>
        """, unsafe_allow_html=True)

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create a modern, branded metric card"""
    delta_html = ""
    if delta:
        delta_html = f'<div class="card-delta">{delta}</div>'
    return f"""
    <div class="modern-card">
        <div class="card-title">{title}</div>
        <div class="card-value">{value}</div>
        {delta_html}
    </div>
    """

def create_status_card(status, description, color="green"):
    """Create a modern status card with color dot and description"""
    color_map = {
        "green": "#22c55e",
        "orange": "#f59e42",
        "red": "#ef4444",
        "blue": "#0a7cff"
    }
    dot = f'<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:{color_map.get(color, '#22c55e')};margin-right:8px;vertical-align:middle;"></span>'
    return f"""
    <div class="status-card">
        <div style="font-size:1.1rem;font-weight:600;margin-bottom:0.5rem;">{dot}<span style='vertical-align:middle;'>{status}</span></div>
        <div style="color:var(--brand-secondary-light);font-size:1rem;">{description}</div>
    </div>
    """

def create_alert_card(title, description, level="info"):
    """Create a modern alert card for warnings/errors/info"""
    color_map = {
        "info": "#0a7cff",
        "warning": "#f59e42",
        "error": "#ef4444",
        "success": "#22c55e"
    }
    border = color_map.get(level, "#0a7cff")
    return f"""
    <div class="modern-card" style="border-left:6px solid {border};">
        <div class="card-title" style="color:{border};">{title}</div>
        <div style="color:var(--brand-secondary-light);font-size:1rem;">{description}</div>
    </div>
    """

def create_risk_badge(risk_level):
    """Create a risk level badge"""
    return f'<span class="risk-badge {risk_level.lower()}">{risk_level}</span>'

def create_status_badge(status):
    """Create a status badge"""
    return f'<span class="status-badge {status.lower()}">{status}</span>'

def apply_styling():
    """Apply all styling configurations"""
    # apply_page_config()  # No longer needed
    apply_custom_css()