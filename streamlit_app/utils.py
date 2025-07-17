"""Utility functions for the Streamlit fraud detection app."""

def get_risk_level(ml_score, is_smurfing_rule):
    """Determine risk level based on ML score and smurfing rule."""
    ml_score = ml_score if ml_score is not None else 0.0
    is_smurfing_rule = is_smurfing_rule if is_smurfing_rule is not None else False
    if is_smurfing_rule or ml_score >= 0.9:
        return "Critical"
    elif ml_score >= 0.7:
        return "High"
    elif ml_score >= 0.4:
        return "Medium"
    return "Low"

def create_metric_card(label, value, delta=None, delta_type="neutral"):
    """Create a beautiful metric card"""
    delta_class = f"metric-delta {delta_type}" if delta else ""
    delta_html = f'<div class="{delta_class}">{delta}</div>' if delta else ""
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

def create_status_indicator(status, text):
    """Create a status indicator badge"""
    return f'<span class="status-indicator status-{status}">● {text}</span>'

def create_risk_badge(risk_level, score=None):
    """Create a risk level badge"""
    score_text = f" ({int(score*100)}%)" if score else ""
    return f'<span class="risk-badge {risk_level.lower()}">{risk_level}{score_text}</span>'