"""Data generation functions for creating dummy fraud detection data."""

import pandas as pd
import random
import hashlib
import time
from datetime import datetime, timedelta
import streamlit as st
from .utils import get_risk_level

@st.cache_data(ttl=5)
def generate_dummy_transactions(limit=10):
    """Generate dummy transaction data."""
    current_time = datetime.now()
    transactions = []
    
    for i in range(limit):
        tx_hash = hashlib.sha256(f"tx_{i}_{int(time.time())}".encode()).hexdigest()
        timestamp = (current_time - timedelta(hours=random.uniform(0, 24))).timestamp() * 1000
        total_input_value = random.uniform(1000000, 1000000000)
        total_output_value = total_input_value * random.uniform(0.95, 0.99)
        fee = total_input_value - total_output_value
        ml_score = random.uniform(0.0, 1.0)
        is_smurfing = random.random() > 0.8
        
        transactions.append({
            "Hash": tx_hash,
            "Timestamp": timestamp,
            "Fee": fee,
            "Size": random.randint(200, 2000),
            "NumInputs": random.randint(1, 10),
            "NumOutputs": random.randint(1, 10),
            "TotalInputValue": total_input_value,
            "TotalOutputValue": total_output_value,
            "ML_Score": ml_score,
            "Smurfing_Rule": is_smurfing
        })
    
    df = pd.DataFrame(transactions)
    if not df.empty:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df['TotalInputValueBTC'] = df['TotalInputValue'] / 1e8
        df['TotalOutputValueBTC'] = df['TotalOutputValue'] / 1e8
        df['Risk_Level'] = df.apply(lambda row: get_risk_level(row['ML_Score'], row['Smurfing_Rule']), axis=1)
    return df

@st.cache_data(ttl=10)
def generate_dummy_alerts(limit=100):
    """Generate dummy alert data."""
    current_time = datetime.now()
    alerts = []
    
    for i in range(limit):
        ml_score = random.uniform(0.4, 1.0)
        is_smurfing = random.random() > 0.7
        if ml_score < 0.5 and not is_smurfing:
            continue
        tx_hash = hashlib.sha256(f"alert_{i}_{int(time.time())}".encode()).hexdigest()
        timestamp = (current_time - timedelta(hours=random.uniform(0, 24))).timestamp() * 1000
        total_input_value = random.uniform(1000000, 1000000000)
        total_output_value = total_input_value * random.uniform(0.95, 0.99)
        fee = total_input_value - total_output_value
        
        alerts.append({
            "Hash": tx_hash,
            "Timestamp": timestamp,
            "ML_Score": ml_score,
            "Smurfing_Rule": is_smurfing,
            "Fee": fee,
            "Size": random.randint(200, 2000),
            "FeePerByte": fee / random.randint(200, 2000),
            "TotalInputValue": total_input_value,
            "TotalOutputValue": total_output_value
        })
    
    df = pd.DataFrame(alerts)
    if not df.empty:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df['Risk_Level'] = df.apply(lambda row: get_risk_level(row['ML_Score'], row['Smurfing_Rule']), axis=1)
    return df.head(limit)

@st.cache_data(ttl=60)
def generate_analytics_data():
    """Generate analytics data for charts."""
    current_time = datetime.now()
    
    # Time series data
    hours = []
    risk_scores = []
    transaction_counts = []
    alert_counts = []
    
    for i in range(24):
        hour = current_time - timedelta(hours=i)
        hours.append(hour)
        risk_scores.append(random.uniform(40, 80))
        transaction_counts.append(random.randint(50, 200))
        alert_counts.append(random.randint(0, 15))
    
    return {
        'hours': hours,
        'risk_scores': risk_scores,
        'transaction_counts': transaction_counts,
        'alert_counts': alert_counts
    }