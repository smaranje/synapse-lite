"""Analytics page for fraud trends and patterns."""

import streamlit as st
import numpy as np

def render_analytics():
    """Render the analytics page."""
    st.markdown("# Fraud Analytics")
    st.markdown("### Deep dive into fraud trends and patterns")
    
    # Import here to avoid circular imports
    from ..data_generator import generate_dummy_transactions, generate_dummy_alerts, generate_analytics_data
    from ..charts import create_advanced_charts, create_ml_score_histogram, create_transaction_scatter
    from ..utils import create_risk_badge
    
    # Create comprehensive analytics
    fig_risk, fig_volume, fig_pie = create_advanced_charts()
    
    # Advanced charts
    chart_tabs = st.tabs(["Risk Trends", "Transaction Volume", "Alert Distribution", "Pattern Analysis"])
    
    with chart_tabs[0]:
        st.plotly_chart(fig_risk, use_container_width=True)
        
        # Additional risk metrics
        risk_col1, risk_col2 = st.columns(2)
        
        with risk_col1:
            st.markdown("### Risk Score Statistics")
            data = generate_analytics_data()
            avg_risk = np.mean(data['risk_scores'])
            max_risk = np.max(data['risk_scores'])
            min_risk = np.min(data['risk_scores'])
            
            st.markdown(f"""
            <div class="chart-container">
                <p><strong>Average Risk Score:</strong> {avg_risk:.1f}%</p>
                <p><strong>Peak Risk Score:</strong> {max_risk:.1f}%</p>
                <p><strong>Lowest Risk Score:</strong> {min_risk:.1f}%</p>
                <p><strong>Risk Volatility:</strong> {np.std(data['risk_scores']):.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with risk_col2:
            st.markdown("### Risk Level Distribution")
            alerts = generate_dummy_alerts(100)
            risk_dist = alerts['Risk_Level'].value_counts()
            
            st.markdown(f"""
            <div class="chart-container">
                <p>{create_risk_badge('Critical')} {risk_dist.get('Critical', 0)} alerts</p>
                <p>{create_risk_badge('High')} {risk_dist.get('High', 0)} alerts</p>
                <p>{create_risk_badge('Medium')} {risk_dist.get('Medium', 0)} alerts</p>
                <p>{create_risk_badge('Low')} {risk_dist.get('Low', 0)} alerts</p>
            </div>
            """, unsafe_allow_html=True)
    
    with chart_tabs[1]:
        st.plotly_chart(fig_volume, use_container_width=True)
        
        # Transaction insights
        st.markdown("### Transaction Insights")
        data = generate_analytics_data()
        total_tx = sum(data['transaction_counts'])
        avg_tx = np.mean(data['transaction_counts'])
        
        from ..utils import create_metric_card
        
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.markdown(create_metric_card("Total Transactions (24h)", f"{total_tx:,}", f"Avg: {avg_tx:.0f}/hour", "positive"), unsafe_allow_html=True)
        
        with insight_col2:
            peak_hour = data['hours'][np.argmax(data['transaction_counts'])]
            st.markdown(create_metric_card("Peak Hour", peak_hour.strftime('%H:%M'), f"{max(data['transaction_counts'])} transactions", "neutral"), unsafe_allow_html=True)
    
    with chart_tabs[2]:
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Alert analysis
        st.markdown("### Alert Analysis")
        alerts = generate_dummy_alerts(100)
        
        analysis_col1, analysis_col2 = st.columns(2)
        
        with analysis_col1:
            st.markdown("#### Alert Triggers")
            smurfing_alerts = len(alerts[alerts['Smurfing_Rule'] == True])
            ml_alerts = len(alerts[alerts['ML_Score'] >= 0.9])
            
            st.markdown(f"""
            <div class="chart-container">
                <p><strong>Smurfing Rule Triggers:</strong> {smurfing_alerts}</p>
                <p><strong>High ML Score Alerts:</strong> {ml_alerts}</p>
                <p><strong>Combined Triggers:</strong> {len(alerts[(alerts['Smurfing_Rule'] == True) & (alerts['ML_Score'] >= 0.9)])}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with analysis_col2:
            st.markdown("#### Alert Timing")
            hourly_alerts = alerts.groupby(alerts['Timestamp'].dt.hour).size()
            peak_alert_hour = hourly_alerts.idxmax()
            
            st.markdown(f"""
            <div class="chart-container">
                <p><strong>Peak Alert Hour:</strong> {peak_alert_hour:02d}:00</p>
                <p><strong>Alerts at Peak:</strong> {hourly_alerts.max()}</p>
                <p><strong>Quietest Hour:</strong> {hourly_alerts.idxmin():02d}:00</p>
            </div>
            """, unsafe_allow_html=True)
    
    with chart_tabs[3]:
        st.markdown("### Pattern Analysis")
        
        # Create pattern analysis charts
        transactions = generate_dummy_transactions(100)
        
        # ML Score distribution
        fig_ml = create_ml_score_histogram(transactions)
        st.plotly_chart(fig_ml, use_container_width=True)
        
        # Transaction size vs risk
        fig_scatter = create_transaction_scatter(transactions)
        st.plotly_chart(fig_scatter, use_container_width=True)