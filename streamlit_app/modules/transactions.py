"""
Transactions page for the Synapse-Lite Fraud Detection System
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import service_integration

def show():
    """Display the transactions monitoring page"""
    st.title("Transaction Monitor")
    
    # Filters section
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "Search by hash or address",
            placeholder="Enter transaction hash or Bitcoin address...",
            key="tx_search"
        )
    
    with col2:
        risk_filter = st.selectbox(
            "Risk Level",
            ["All", "Critical", "High", "Medium", "Low"],
            key="risk_filter"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Timestamp", "Value", "Risk Score"],
            key="sort_by"
        )
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Refresh", key="refresh_tx"):
            st.rerun()
    
    # Apply filters
    filtered_transactions = st.session_state.transactions.copy()
    
    if search_query:
        filtered_transactions = [
            tx for tx in filtered_transactions
            if search_query.lower() in tx['hash'].lower() or
            any(search_query.lower() in addr.lower() for addr in tx.get('input_addresses', []) + tx.get('output_addresses', []))
        ]
    
    if risk_filter != "All":
        filtered_transactions = [
            tx for tx in filtered_transactions
            if tx['risk_level'] == risk_filter
        ]
    
    # Sort transactions
    if sort_by == "Timestamp":
        filtered_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
    elif sort_by == "Value":
        filtered_transactions.sort(key=lambda x: x['total_value_btc'], reverse=True)
    elif sort_by == "Risk Score":
        filtered_transactions.sort(key=lambda x: x['ml_score'], reverse=True)
    
    # Summary metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Transactions", f"{len(filtered_transactions):,}")
    
    with col2:
        total_volume = sum(tx['total_value_btc'] for tx in filtered_transactions)
        st.metric("Total Volume", f"{total_volume:.2f} BTC")
    
    with col3:
        high_risk_count = len([tx for tx in filtered_transactions if tx['risk_level'] in ['Critical', 'High']])
        st.metric("High Risk", high_risk_count)
    
    with col4:
        avg_score = sum(tx['ml_score'] for tx in filtered_transactions) / len(filtered_transactions) if filtered_transactions else 0
        st.metric("Avg Risk Score", f"{avg_score:.2%}")
    
    # Transaction list
    st.markdown("---")
    st.markdown(f"### Showing {len(filtered_transactions)} transactions")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Card View", "Table View", "Analytics"])
    
    with tab1:
        # Card view
        for i, tx in enumerate(filtered_transactions[:50]):  # Limit to 50 for performance
            risk_colors = {
                'Critical': '#FF5252',
                'High': '#FF9800',
                'Medium': '#FFC107',
                'Low': '#00D395'
            }
            
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])
                
                with col1:
                    # Make hash more readable with better formatting
                    hash_display = f"{tx['hash'][:8]}...{tx['hash'][-6:]}"
                    st.markdown(f"**Hash:** `{hash_display}`")
                    st.caption(f"Time: {tx['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                with col2:
                    st.markdown(f"**Value:** {tx['total_value_btc']:.6f} BTC")
                    st.caption(f"${tx['total_value_usd']:,.2f} USD")
                
                with col3:
                    st.markdown(f"**ML Score:** {tx['ml_score']:.2%}")
                    if tx['is_smurfing_rule']:
                        st.caption("Smurfing detected")
                
                with col4:
                    st.markdown(
                        f'<div class="risk-badge-clean" data-risk="{tx["risk_level"]}">{tx["risk_level"]}</div>',
                        unsafe_allow_html=True
                    )
                
                with col5:
                    if st.button("Details", key=f"details_{i}", use_container_width=True):
                        st.session_state[f'show_details_{i}'] = True
                
                # Show details below the transaction card if button was clicked
                if st.session_state.get(f'show_details_{i}', False):
                    with st.expander("Transaction Details", expanded=True):
                        detail_col1, detail_col2, detail_col3 = st.columns(3)
                        with detail_col1:
                            st.metric("Fee", f"{tx['fee']:.8f} BTC")
                            st.metric("Size", f"{tx.get('size', 'N/A')} bytes")
                        with detail_col2:
                            st.metric("Inputs", tx['num_inputs'])
                            st.metric("Outputs", tx['num_outputs'])
                        with detail_col3:
                            st.metric("Risk Score", f"{tx['ml_score']:.2%}")
                            st.metric("Smurfing", "Yes" if tx['is_smurfing_rule'] else "No")
                
                st.markdown("---")
    
    with tab2:
        # Table view
        if filtered_transactions:
            df = pd.DataFrame(filtered_transactions)
            
            # Select and rename columns for display
            display_columns = {
                'hash': 'Transaction Hash',
                'timestamp': 'Time',
                'total_value_btc': 'Value (BTC)',
                'total_value_usd': 'Value (USD)',
                'ml_score': 'Risk Score',
                'risk_level': 'Risk Level',
                'num_inputs': 'Inputs',
                'num_outputs': 'Outputs',
                'is_smurfing_rule': 'Smurfing'
            }
            
            df_display = df[list(display_columns.keys())].copy()
            df_display.columns = list(display_columns.values())
            
            # Format columns
            df_display['Transaction Hash'] = df_display['Transaction Hash'].apply(lambda x: f"{x[:8]}...{x[-6:]}")
            df_display['Time'] = pd.to_datetime(df_display['Time']).dt.strftime('%Y-%m-%d %H:%M')
            df_display['Value (BTC)'] = df_display['Value (BTC)'].apply(lambda x: f"{x:.6f}")
            df_display['Value (USD)'] = df_display['Value (USD)'].apply(lambda x: f"${x:,.2f}")
            df_display['Risk Score'] = df_display['Risk Score'].apply(lambda x: f"{x:.2%}")
            df_display['Smurfing'] = df_display['Smurfing'].apply(lambda x: "Yes" if x else "No")
            
            # Apply color coding to risk level
            def color_risk_level(val):
                colors = {
                    'Critical': 'background-color: #FF5252; color: white;',
                    'High': 'background-color: #FF9800; color: white;',
                    'Medium': 'background-color: #FFC107; color: black;',
                    'Low': 'background-color: #00D395; color: white;'
                }
                return colors.get(val, '')
            
            styled_df = df_display.style.applymap(color_risk_level, subset=['Risk Level'])
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=600
            )
            
            # Export functionality
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No transactions found matching the filters.")
    
    with tab3:
        # Analytics view
        if filtered_transactions:
            # Risk distribution over time
            st.subheader("Risk Score Distribution Over Time")
            
            df_analytics = pd.DataFrame(filtered_transactions)
            df_analytics['hour'] = pd.to_datetime(df_analytics['timestamp']).dt.floor('H')
            
            hourly_risk = df_analytics.groupby(['hour', 'risk_level']).size().reset_index(name='count')
            
            fig = px.area(
                hourly_risk,
                x='hour',
                y='count',
                color='risk_level',
                color_discrete_map={
                    'Critical': '#FF5252',
                    'High': '#FF9800',
                    'Medium': '#FFC107',
                    'Low': '#00D395'
                },
                title="Transaction Risk Levels Over Time"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Value distribution
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Transaction Value Distribution")
                fig = px.histogram(
                    df_analytics,
                    x='total_value_btc',
                    nbins=30,
                    title="Distribution of Transaction Values"
                )
                fig.update_traces(marker_color='#0052FF')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Risk Score vs Transaction Value")
                fig = px.scatter(
                    df_analytics,
                    x='total_value_btc',
                    y='ml_score',
                    color='risk_level',
                    color_discrete_map={
                        'Critical': '#FF5252',
                        'High': '#FF9800',
                        'Medium': '#FFC107',
                        'Low': '#00D395'
                    },
                    title="Risk Score vs Transaction Value",
                    labels={'ml_score': 'Risk Score', 'total_value_btc': 'Value (BTC)'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for analytics.")
    
    # Real-time updates indicator
    if not st.session_state.USE_DUMMY_DATA:
        kafka_conn = service_integration.get_kafka_connection()
        if kafka_conn.create_consumer():
            with st.empty():
                st.info("Listening for real-time updates from Kafka...")
                # This would be replaced with actual Kafka consumer logic in production