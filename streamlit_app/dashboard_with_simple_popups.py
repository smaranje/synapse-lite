"""
Simple Streamlit Dashboard with Clean Loading Messages
User-friendly data refresh notifications
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import os

# Simple page config
st.set_page_config(
    page_title="Fraud Detection Dashboard",
    page_icon="🔍",
    layout="wide"
)

# Simple CSS for clean popups
st.markdown("""
<style>
.simple-popup {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    color: #333;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    border-left: 4px solid #4CAF50;
    z-index: 1000;
    font-size: 14px;
    max-width: 300px;
}

.popup-loading {
    border-left-color: #2196F3;
}

.popup-success {
    border-left-color: #4CAF50;
}

.popup-info {
    border-left-color: #FF9800;
}

.loading-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #2196F3;
    margin-right: 8px;
    animation: pulse 1.5s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

def show_simple_message(message, msg_type="info", duration=3):
    """Show a simple, clean message popup"""
    popup_class = f"simple-popup popup-{msg_type}"
    
    if msg_type == "loading":
        icon = '<div class="loading-dot"></div>'
    elif msg_type == "success":
        icon = "✅ "
    else:
        icon = "ℹ️ "
    
    popup_html = f"""
    <div class="{popup_class}" id="message-popup">
        {icon}{message}
    </div>
    <script>
        setTimeout(function() {{
            var popup = document.getElementById('message-popup');
            if (popup) popup.remove();
        }}, {duration * 1000});
    </script>
    """
    return st.markdown(popup_html, unsafe_allow_html=True)

def generate_sample_data():
    """Generate some sample transaction data"""
    import random
    
    transactions = []
    for i in range(20):
        transactions.append({
            'id': f"tx_{i+1}",
            'amount': random.randint(100, 10000),
            'risk_score': random.randint(1, 100),
            'status': random.choice(['Normal', 'Suspicious', 'Flagged']),
            'time': datetime.now() - timedelta(minutes=random.randint(1, 60))
        })
    return transactions

def load_data():
    """Load data with simple user feedback"""
    
    # Show loading message
    message_placeholder = st.empty()
    with message_placeholder:
        show_simple_message("Loading transaction data...", "loading")
    
    # Simulate data loading
    time.sleep(1.5)
    
    # Get fresh data
    new_data = generate_sample_data()
    
    # Show success message
    with message_placeholder:
        show_simple_message(f"Loaded {len(new_data)} transactions", "success")
    
    # Clear message after showing
    time.sleep(1)
    message_placeholder.empty()
    
    return new_data

# Auto-refresh data every 30 seconds
if st.session_state.last_refresh < datetime.now() - timedelta(seconds=30):
    st.session_state.transactions = load_data()
    st.session_state.last_refresh = datetime.now()

# Header
st.title("🔍 Fraud Detection Dashboard")
st.markdown("---")

# Simple status indicator
col1, col2, col3 = st.columns(3)

with col1:
    if st.session_state.transactions:
        st.success("✅ Data Loaded")
    else:
        st.warning("⏳ Loading...")

with col2:
    total_transactions = len(st.session_state.transactions)
    st.metric("Total Transactions", total_transactions)

with col3:
    last_update = st.session_state.last_refresh.strftime("%H:%M:%S")
    st.info(f"🕒 Last Updated: {last_update}")

# Refresh button
if st.button("🔄 Refresh Data", use_container_width=True):
    st.session_state.transactions = load_data()
    st.session_state.last_refresh = datetime.now()
    st.rerun()

# Display data
if st.session_state.transactions:
    st.markdown("### Recent Transactions")
    
    # Convert to DataFrame for display
    df = pd.DataFrame(st.session_state.transactions)
    
    # Simple data display
    for i, tx in enumerate(st.session_state.transactions[:10]):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.write(f"**{tx['id']}**")
        
        with col2:
            st.write(f"${tx['amount']:,}")
        
        with col3:
            if tx['status'] == 'Normal':
                st.success(tx['status'])
            elif tx['status'] == 'Suspicious':
                st.warning(tx['status'])
            else:
                st.error(tx['status'])
        
        with col4:
            risk_color = "🟢" if tx['risk_score'] < 30 else "🟡" if tx['risk_score'] < 70 else "🔴"
            st.write(f"{risk_color} {tx['risk_score']}%")
        
        if i < 9:  # Don't add divider after last item
            st.markdown("---")

else:
    st.info("📊 No transaction data available yet. Click 'Refresh Data' to load.")

# Simple footer
st.markdown("---")
st.markdown("*Data refreshes automatically every 30 seconds*")