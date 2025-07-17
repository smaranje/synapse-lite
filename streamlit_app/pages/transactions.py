"""
Transactions Page for Synapse-Lite
Transaction search, analysis, and detailed views
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

class TransactionsPage:
    """Transactions page implementation"""
    
    def __init__(self, app_state):
        self.app_state = app_state
    
    def render(self):
        """Render the transactions page"""
        self._render_search_filters()
        self._render_transaction_summary()
        self._render_transaction_table()
        self._render_transaction_analytics()
    
    def _render_search_filters(self):
        """Render search and filter controls"""
        st.markdown("## 💰 Transaction Analysis")
        
        with st.expander("🔍 Search & Filters", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                search_term = st.text_input("Search Hash/Address", placeholder="Enter transaction hash or address...")
            
            with col2:
                risk_threshold = st.slider("Min Risk Score", 0, 100, 0, help="Filter by minimum risk score")
            
            with col3:
                status_filter = st.selectbox("Status", ["all", "confirmed", "pending", "flagged", "review"])
            
            with col4:
                date_range = st.selectbox("Time Range", ["1 hour", "24 hours", "7 days", "30 days", "All"])
        
        # Apply filters and search
        self._apply_filters(search_term, risk_threshold, status_filter, date_range)
    
    def _apply_filters(self, search_term, risk_threshold, status_filter, date_range):
        """Apply search filters and update session state"""
        from data.data_service import DataService
        data_service = DataService()
        
        # Calculate date range
        date_from = None
        if date_range == "1 hour":
            date_from = datetime.now() - timedelta(hours=1)
        elif date_range == "24 hours":
            date_from = datetime.now() - timedelta(days=1)
        elif date_range == "7 days":
            date_from = datetime.now() - timedelta(days=7)
        elif date_range == "30 days":
            date_from = datetime.now() - timedelta(days=30)
        
        # Search transactions
        filtered_transactions = data_service.search_transactions(
            search_term=search_term,
            risk_threshold=risk_threshold,
            date_from=date_from,
            status_filter=status_filter
        )
        
        # Store in session state
        st.session_state.filtered_transactions = filtered_transactions
    
    def _render_transaction_summary(self):
        """Render transaction summary metrics"""
        filtered_txns = st.session_state.get('filtered_transactions', [])
        
        if filtered_txns:
            col1, col2, col3, col4 = st.columns(4)
            
            # Calculate summary stats
            total_count = len(filtered_txns)
            total_volume = sum([t.get('amount_usd', 0) for t in filtered_txns])
            avg_amount = total_volume / total_count if total_count > 0 else 0
            high_risk_count = len([t for t in filtered_txns if t.get('risk_score', 0) > 80])
            
            with col1:
                st.metric("Total Transactions", f"{total_count:,}")
            
            with col2:
                st.metric("Total Volume", f"${total_volume:,.2f}")
            
            with col3:
                st.metric("Average Amount", f"${avg_amount:,.2f}")
            
            with col4:
                high_risk_pct = (high_risk_count / total_count * 100) if total_count > 0 else 0
                st.metric("High Risk", f"{high_risk_count}", delta=f"{high_risk_pct:.1f}%")
    
    def _render_transaction_table(self):
        """Render searchable transaction table"""
        st.markdown("### Transaction Details")
        
        filtered_txns = st.session_state.get('filtered_transactions', [])
        
        if filtered_txns:
            # Convert to DataFrame for display
            df_data = []
            for txn in filtered_txns:
                timestamp = datetime.fromisoformat(txn.get('timestamp', ''))
                df_data.append({
                    'Time': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'Hash': txn.get('hash', '')[:16] + '...',
                    'Amount (USD)': f"${txn.get('amount_usd', 0):,.2f}",
                    'Amount (BTC)': f"{txn.get('amount_btc', 0):.8f}",
                    'Risk Score': txn.get('risk_score', 0),
                    'Status': txn.get('status', 'unknown').title(),
                    'Country': txn.get('country', 'Unknown'),
                    'Confirmations': txn.get('confirmations', 0)
                })
            
            df = pd.DataFrame(df_data)
            
            # Display with styling
            styled_df = df.style.apply(self._style_risk_score, subset=['Risk Score'])
            st.dataframe(styled_df, use_container_width=True, height=400)
            
            # Transaction details modal
            if st.button("View Selected Transaction Details"):
                self._show_transaction_modal(filtered_txns[0])  # Show first transaction as example
            
        else:
            st.info("No transactions found matching the current filters.")
    
    def _style_risk_score(self, val):
        """Style risk score column based on value"""
        styles = []
        for score in val:
            if score > 80:
                styles.append('background-color: #ff4757; color: white;')
            elif score > 60:
                styles.append('background-color: #ff9500; color: white;')
            elif score > 40:
                styles.append('background-color: #ffa502; color: black;')
            else:
                styles.append('background-color: #2ed573; color: white;')
        return styles
    
    def _show_transaction_modal(self, transaction):
        """Show detailed transaction information"""
        st.markdown("#### Transaction Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Information**")
            st.text(f"Hash: {transaction.get('hash', 'N/A')}")
            st.text(f"Block Height: {transaction.get('block_height', 'N/A')}")
            st.text(f"Confirmations: {transaction.get('confirmations', 0)}")
            st.text(f"Size: {transaction.get('size_bytes', 0)} bytes")
            st.text(f"Fee: ${transaction.get('fee_usd', 0):.2f}")
            
            st.markdown("**Addresses**")
            st.text(f"From: {transaction.get('from_address', 'N/A')}")
            st.text(f"To: {transaction.get('to_address', 'N/A')}")
        
        with col2:
            st.markdown("**Risk Analysis**")
            risk_score = transaction.get('risk_score', 0)
            st.progress(risk_score / 100, text=f"Risk Score: {risk_score}/100")
            
            risk_factors = transaction.get('risk_factors', [])
            if risk_factors:
                st.markdown("**Risk Factors:**")
                for factor in risk_factors:
                    st.text(f"• {factor}")
            
            st.markdown("**Geographic Info**")
            st.text(f"Country: {transaction.get('country', 'Unknown')}")
            st.text(f"Wallet Type: {transaction.get('wallet_type', 'Unknown')}")
    
    def _render_transaction_analytics(self):
        """Render transaction analytics charts"""
        st.markdown("### Transaction Analytics")
        
        filtered_txns = st.session_state.get('filtered_transactions', [])
        
        if filtered_txns and len(filtered_txns) > 5:
            col1, col2 = st.columns(2)
            
            with col1:
                self._render_amount_distribution()
            
            with col2:
                self._render_risk_score_distribution()
            
            # Time series analysis
            self._render_transaction_timeline()
            
        else:
            st.info("Need more transaction data for analytics visualization.")
    
    def _render_amount_distribution(self):
        """Render transaction amount distribution"""
        filtered_txns = st.session_state.get('filtered_transactions', [])
        amounts = [t.get('amount_usd', 0) for t in filtered_txns]
        
        fig = px.histogram(
            x=amounts,
            nbins=20,
            title="Transaction Amount Distribution",
            labels={'x': 'Amount (USD)', 'y': 'Frequency'}
        )
        
        fig.update_layout(
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_risk_score_distribution(self):
        """Render risk score distribution"""
        filtered_txns = st.session_state.get('filtered_transactions', [])
        risk_scores = [t.get('risk_score', 0) for t in filtered_txns]
        
        fig = px.histogram(
            x=risk_scores,
            nbins=10,
            title="Risk Score Distribution",
            labels={'x': 'Risk Score', 'y': 'Count'},
            color_discrete_sequence=['#ff4757']
        )
        
        fig.update_layout(
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_transaction_timeline(self):
        """Render transaction timeline"""
        filtered_txns = st.session_state.get('filtered_transactions', [])
        
        # Group by hour
        timeline_data = {}
        for txn in filtered_txns:
            timestamp = datetime.fromisoformat(txn.get('timestamp', ''))
            hour_key = timestamp.strftime('%Y-%m-%d %H:00')
            
            if hour_key not in timeline_data:
                timeline_data[hour_key] = {'count': 0, 'volume': 0, 'risk_sum': 0}
            
            timeline_data[hour_key]['count'] += 1
            timeline_data[hour_key]['volume'] += txn.get('amount_usd', 0)
            timeline_data[hour_key]['risk_sum'] += txn.get('risk_score', 0)
        
        # Convert to lists for plotting
        times = list(timeline_data.keys())
        counts = [timeline_data[t]['count'] for t in times]
        volumes = [timeline_data[t]['volume'] for t in times]
        avg_risks = [timeline_data[t]['risk_sum'] / timeline_data[t]['count'] for t in times]
        
        # Create subplot with secondary y-axis
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=times,
            y=counts,
            mode='lines+markers',
            name='Transaction Count',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=times,
            y=volumes,
            mode='lines+markers',
            name='Volume (USD)',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Transaction Timeline",
            xaxis_title="Time",
            yaxis=dict(title="Count", side="left"),
            yaxis2=dict(title="Volume (USD)", side="right", overlaying="y"),
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)