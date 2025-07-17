"""Transactions page for monitoring Bitcoin transactions."""

import streamlit as st

def render_transactions():
    """Render the transactions monitoring page."""
    st.markdown("# Transaction Monitor")
    st.markdown("### Real-time Bitcoin transaction analysis")
    
    # Import here to avoid circular imports
    from ..data_generator import generate_dummy_transactions
    from ..utils import create_risk_badge, get_risk_level
    from ..config import BTC_USD_RATE
    
    # Controls
    control_col1, control_col2, control_col3 = st.columns([2, 1, 1])
    
    with control_col1:
        search_term = st.text_input("Search transactions", placeholder="Enter hash, address, or amount")
    with control_col2:
        risk_filter = st.selectbox("Risk Level", ["All", "Critical", "High", "Medium", "Low"])
    with control_col3:
        if st.button("Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Transaction table
    transactions = generate_dummy_transactions(20)
    
    if not transactions.empty:
        # Apply filters
        if risk_filter != "All":
            transactions = transactions[transactions['Risk_Level'] == risk_filter]
        if search_term:
            transactions = transactions[transactions['Hash'].str.contains(search_term, case=False, na=False)]
        
        # Display transactions
        for _, tx in transactions.iterrows():
            risk_level = get_risk_level(tx['ML_Score'], tx['Smurfing_Rule'])
            st.markdown(f"""
            <div class="transaction-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 1.1rem;">{tx['Hash'][:16]}...</div>
                        <div style="color: #a0aec0; font-size: 0.9rem; margin: 0.25rem 0;">
                            {tx['NumInputs']} inputs → {tx['NumOutputs']} outputs
                        </div>
                        <div style="color: #63b3ed; font-weight: 500;">
                            {tx['TotalOutputValueBTC']:.4f} BTC (${tx['TotalOutputValueBTC'] * BTC_USD_RATE:,.2f})
                        </div>
                    </div>
                    <div style="text-align: right;">
                        {create_risk_badge(risk_level, tx['ML_Score'])}
                        <div style="color: #a0aec0; font-size: 0.8rem; margin-top: 0.5rem;">
                            {tx['Timestamp'].strftime('%H:%M:%S')}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No transactions found matching your criteria.")