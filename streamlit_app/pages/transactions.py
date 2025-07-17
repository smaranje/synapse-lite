# Transactions page module - Coinbase Business Style

import streamlit as st
import sys
import os
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_generator import generate_transaction_data, get_risk_level, format_currency, format_hash
from styling import create_status_badge, create_risk_badge

def render_transactions():
    """Render the transactions monitoring page in Coinbase Business style"""
    
    # Page header
    st.markdown("""
    <div class="cb-card" style="margin-bottom: 2rem;">
        <h1 style="margin: 0; font-size: 1.875rem; font-weight: 700; color: var(--cb-gray-900);">Transactions</h1>
        <p style="margin: 0.5rem 0 0 0; color: var(--cb-gray-600); font-size: 1rem;">Monitor and analyze transaction activity</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filters in a clean card
    st.markdown('<div class="cb-card">', unsafe_allow_html=True)
    st.markdown("**Filters**")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        search_term = st.text_input("Search transactions", placeholder="Hash, amount, or status...", label_visibility="collapsed")
    
    with col2:
        status_filter = st.selectbox("Status", ["All", "Confirmed", "Pending", "Flagged"], label_visibility="collapsed")
    
    with col3:
        min_risk = st.slider("Min Risk Score", 0, 100, 0, label_visibility="collapsed")
    
    with col4:
        max_amount = st.number_input("Max Amount (BTC)", value=10.0, min_value=0.0, label_visibility="collapsed")
    
    # Action buttons
    col_btn1, col_btn2, col_spacer = st.columns([1, 1, 3])
    with col_btn1:
        refresh_clicked = st.button("🔄 Refresh", type="primary", use_container_width=True)
    with col_btn2:
        export_clicked = st.button("📊 Export", type="secondary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if refresh_clicked:
        st.cache_data.clear()
        st.rerun()
    
    # Generate and filter transaction data
    df = generate_transaction_data(100)
    
    # Apply filters
    filtered_df = df.copy()
    
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df["Status"] == status_filter]
    
    if search_term:
        search_mask = (
            filtered_df["Hash"].str.contains(search_term, case=False, na=False) |
            filtered_df["Status"].str.contains(search_term, case=False, na=False) |
            filtered_df["Amount (BTC)"].astype(str).str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    filtered_df = filtered_df[filtered_df["Risk Score"] >= min_risk]
    filtered_df = filtered_df[filtered_df["Amount (BTC)"] <= max_amount]
    
    # Summary stats
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.markdown(f"""
        <div class="cb-metric-card">
            <div class="cb-metric-label">Total Transactions</div>
            <div class="cb-metric-value">{len(filtered_df):,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_stat2:
        total_amount = filtered_df["Amount (BTC)"].sum()
        st.markdown(f"""
        <div class="cb-metric-card">
            <div class="cb-metric-label">Total Volume</div>
            <div class="cb-metric-value">{total_amount:.2f} BTC</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_stat3:
        avg_risk = filtered_df["Risk Score"].mean() if len(filtered_df) > 0 else 0
        st.markdown(f"""
        <div class="cb-metric-card">
            <div class="cb-metric-label">Avg Risk Score</div>
            <div class="cb-metric-value">{avg_risk:.1f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_stat4:
        high_risk_count = len(filtered_df[filtered_df["Risk Score"] >= 70])
        st.markdown(f"""
        <div class="cb-metric-card">
            <div class="cb-metric-label">High Risk</div>
            <div class="cb-metric-value">{high_risk_count}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Transactions table in Coinbase style
    st.markdown('<div class="cb-card">', unsafe_allow_html=True)
    st.markdown("**Transaction History**")
    
    if len(filtered_df) == 0:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 0; color: var(--cb-gray-500);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
            <div style="font-size: 1.125rem; font-weight: 600; margin-bottom: 0.5rem;">No transactions found</div>
            <div>Try adjusting your filters or search terms</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Prepare display data
        display_df = filtered_df.copy()
        
        # Format the data for display
        display_df["Transaction Hash"] = display_df["Hash"].apply(lambda x: f"{x[:8]}...{x[-8:]}")
        display_df["Amount"] = display_df["Amount (BTC)"].apply(lambda x: f"{x:.4f} BTC")
        display_df["USD Value"] = display_df["Amount (BTC)"].apply(lambda x: f"${x * 45000:.2f}")
        
        # Create formatted status and risk columns
        def format_status(status):
            return f'<span class="cb-badge {status.lower()}">{status}</span>'
        
        def format_risk(risk_score):
            risk_level = get_risk_level(risk_score)
            return f'<span class="cb-badge {risk_level.lower()}">{risk_level}</span>'
        
        # Select and reorder columns for display
        display_columns = [
            "Transaction Hash", "Amount", "USD Value", "Status", "Risk Score", "Timestamp"
        ]
        
        # Create the table with custom styling
        for idx, row in display_df.iterrows():
            st.markdown(f"""
            <div style="border-bottom: 1px solid var(--cb-gray-200); padding: 1rem 0; display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1.5fr; gap: 1rem; align-items: center;">
                <div>
                    <div style="font-weight: 600; color: var(--cb-gray-900); margin-bottom: 0.25rem;">{row['Transaction Hash']}</div>
                    <div style="font-size: 0.75rem; color: var(--cb-gray-500);">{row['Hash'][:16]}...</div>
                </div>
                <div>
                    <div style="font-weight: 600; color: var(--cb-gray-900);">{row['Amount (BTC)']:.4f} BTC</div>
                    <div style="font-size: 0.875rem; color: var(--cb-gray-500);">${row['Amount (BTC)'] * 45000:.2f}</div>
                </div>
                <div>
                    {format_status(row['Status'])}
                </div>
                <div>
                    <div style="font-weight: 600; color: var(--cb-gray-900);">{row['Risk Score']}</div>
                    <div>{format_risk(row['Risk Score'])}</div>
                </div>
                <div style="font-size: 0.875rem; color: var(--cb-gray-600);">
                    {row['Timestamp'].strftime('%Y-%m-%d %H:%M')}
                </div>
                <div>
                    <button style="background: var(--cb-blue); color: white; border: none; border-radius: 6px; padding: 0.5rem 1rem; font-size: 0.75rem; cursor: pointer;">View Details</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Pagination info
    if len(filtered_df) > 0:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0; color: var(--cb-gray-500); font-size: 0.875rem;">
            Showing {min(len(filtered_df), 50)} of {len(filtered_df)} transactions
        </div>
        """, unsafe_allow_html=True)