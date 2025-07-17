# Transactions page module

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_generator import generate_transaction_data, get_risk_level, format_currency, format_hash
from styling import create_status_badge, create_risk_badge

def render_transactions():
    """Render the transactions monitoring page"""
    st.title("💰 Transactions")
    st.markdown("### Recent Bitcoin Transaction Monitoring")
    
    # Control panel
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search transactions", placeholder="Hash, amount, or status...")
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "Confirmed", "Pending", "Flagged"])
    
    with col3:
        min_risk = st.slider("Min Risk Score", 0, 100, 0)
    
    with col4:
        max_amount = st.number_input("Max Amount (BTC)", value=10.0, min_value=0.0)
    
    # Refresh button
    if st.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Generate and filter transaction data
    df = generate_transaction_data(100)
    
    # Apply filters
    filtered_df = df.copy()
    
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]
    
    filtered_df = filtered_df[filtered_df["Risk Score"] >= min_risk]
    filtered_df = filtered_df[filtered_df["Amount (BTC)"] <= max_amount]
    
    if search_term:
        search_mask = (
            filtered_df["Hash"].str.contains(search_term, case=False, na=False) |
            filtered_df["ID"].str.contains(search_term, case=False, na=False) |
            filtered_df["Status"].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    # Summary statistics
    st.markdown("## Transaction Summary")

    # Debug: Show first few rows of filtered_df
    st.write("Filtered transactions (head):", filtered_df.head())

    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Total Transactions", len(filtered_df))
    
    with summary_col2:
        total_volume = filtered_df["Amount (BTC)"].sum()
        st.metric("Total Volume", f"₿{total_volume:.4f}")
    
    with summary_col3:
        avg_risk = filtered_df["Risk Score"].mean() if len(filtered_df) > 0 else 0
        st.metric("Average Risk Score", f"{avg_risk:.1f}%")
    
    with summary_col4:
        high_risk_count = len(filtered_df[filtered_df["Risk Score"] >= 80])
        st.metric("High Risk Transactions", high_risk_count)
    
    st.markdown("---")
    
    # Transactions table/cards view
    view_type = st.radio("View Type", ["Cards", "Table"], horizontal=True)
    
    if view_type == "Cards":
        # Card view
        if len(filtered_df) > 0:
            for idx, row in filtered_df.head(20).iterrows():  # Limit to 20 for performance
                risk_level = get_risk_level(row["Risk Score"])
                
                # Create transaction card
                st.markdown(f"""
                <div class="transaction-card">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
                        <div style="flex: 1;">
                            <div style="font-weight: 600; font-size: 1rem; color: #1a1a1a; margin-bottom: 0.25rem;">
                                🔗 {format_hash(row['Hash'], 8)}
                            </div>
                            <div style="color: #6b7280; font-size: 0.875rem;">
                                ID: {row['ID']} • {row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            {create_status_badge(row['Status'])}
                            <div style="margin-top: 0.25rem;">
                                {create_risk_badge(risk_level)}
                            </div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
                        <div>
                            <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">Amount</div>
                            <div style="font-weight: 600; color: #0052ff;">₿{row['Amount (BTC)']:.6f}</div>
                            <div style="font-size: 0.875rem; color: #6b7280;">${row['USD Value']:,.2f}</div>
                        </div>
                        
                        <div>
                            <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">Fee</div>
                            <div style="font-weight: 600;">₿{row['Fee (BTC)']:.8f}</div>
                            <div style="font-size: 0.875rem; color: #6b7280;">${row['Fee USD']:.2f}</div>
                        </div>
                        
                        <div>
                            <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">I/O</div>
                            <div style="font-weight: 600;">{row['Input Count']} → {row['Output Count']}</div>
                            <div style="font-size: 0.875rem; color: #6b7280;">{row['Size (bytes)']} bytes</div>
                        </div>
                        
                        <div>
                            <div style="font-size: 0.75rem; color: #6b7280; text-transform: uppercase; font-weight: 600; margin-bottom: 0.25rem;">Risk Score</div>
                            <div style="font-weight: 600; color: {'#dc2626' if row['Risk Score'] >= 80 else '#ea580c' if row['Risk Score'] >= 60 else '#0052ff' if row['Risk Score'] >= 40 else '#059669'};">
                                {row['Risk Score']}%
                            </div>
                            <div style="font-size: 0.875rem; color: #6b7280;">Confirmations: {row['Confirmations']}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No transactions match your current filters.")
    
    else:
        # Table view
        if len(filtered_df) > 0:
            # Prepare display dataframe
            display_df = filtered_df.copy()
            display_df['Hash'] = display_df['Hash'].apply(lambda x: format_hash(x, 6))
            display_df['Risk Level'] = display_df['Risk Score'].apply(get_risk_level)
            display_df['Amount (BTC)'] = display_df['Amount (BTC)'].apply(lambda x: f"₿{x:.6f}")
            display_df['USD Value'] = display_df['USD Value'].apply(lambda x: f"${x:,.2f}")
            display_df['Timestamp'] = display_df['Timestamp'].dt.strftime('%H:%M:%S')
            
            # Select columns for display
            display_columns = [
                'ID', 'Hash', 'Amount (BTC)', 'USD Value', 
                'Status', 'Risk Level', 'Risk Score', 'Timestamp'
            ]
            
            st.dataframe(
                display_df[display_columns],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No transactions match your current filters.")
    
    # Transaction statistics
    if len(filtered_df) > 0:
        st.markdown("---")
        st.markdown("## Transaction Analytics")
        
        analytics_col1, analytics_col2 = st.columns(2)
        
        with analytics_col1:
            st.markdown("### Risk Distribution")
            risk_counts = filtered_df.groupby(filtered_df['Risk Score'].apply(get_risk_level)).size()
            for risk_level, count in risk_counts.items():
                percentage = (count / len(filtered_df)) * 100
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: white; border-radius: 8px; margin: 0.25rem 0; border: 1px solid #f0f3f7;">
                    <span>{create_risk_badge(risk_level)} {risk_level}</span>
                    <span style="font-weight: 600;">{count} ({percentage:.1f}%)</span>
                </div>
                """, unsafe_allow_html=True)
        
        with analytics_col2:
            st.markdown("### Status Breakdown")
            status_counts = filtered_df['Status'].value_counts()
            for status, count in status_counts.items():
                percentage = (count / len(filtered_df)) * 100
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; background: white; border-radius: 8px; margin: 0.25rem 0; border: 1px solid #f0f3f7;">
                    <span>{create_status_badge(status)} {status}</span>
                    <span style="font-weight: 600;">{count} ({percentage:.1f}%)</span>
                </div>
                """, unsafe_allow_html=True)