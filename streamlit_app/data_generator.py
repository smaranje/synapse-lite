# Data generation utilities for Streamlit app

import pandas as pd
import random
import hashlib
import time
from datetime import datetime, timedelta
import numpy as np
from config import BTC_USD_RATE

def generate_transaction_data(count=50):
    """Generate dummy transaction data"""
    transactions = []
    
    for i in range(count):
        tx = {
            "ID": hashlib.md5(f"tx_{i}_{random.randint(1000, 9999)}".encode()).hexdigest()[:8],
            "Hash": hashlib.sha256(f"tx_{i}_{int(time.time())}".encode()).hexdigest(),
            "Amount (BTC)": round(random.uniform(0.001, 10.0), 6),
            "USD Value": 0,  # Will calculate
            "Risk Score": random.randint(1, 100),
            "Status": random.choice(["Confirmed", "Pending", "Flagged"]),
            "Timestamp": datetime.now() - timedelta(minutes=random.randint(1, 1440)),
            "Fee (BTC)": round(random.uniform(0.0001, 0.01), 8),
            "Confirmations": random.randint(0, 6),
            "Size (bytes)": random.randint(250, 2000),
            "Input Count": random.randint(1, 5),
            "Output Count": random.randint(1, 8)
        }
        tx["USD Value"] = round(tx["Amount (BTC)"] * BTC_USD_RATE, 2)
        tx["Fee USD"] = round(tx["Fee (BTC)"] * BTC_USD_RATE, 2)
        transactions.append(tx)
    
    return pd.DataFrame(transactions)

def generate_alert_data(count=15):
    """Generate dummy fraud alert data"""
    alerts = []
    alert_types = [
        "Suspicious Pattern", 
        "High-Risk Transaction", 
        "Account Anomaly", 
        "Multiple Failures",
        "Unusual Velocity",
        "Smurfing Activity",
        "Round Amount Pattern",
        "Velocity Check Failed"
    ]
    
    for i in range(count):
        alert = {
            "ID": f"ALERT-{random.randint(1000, 9999)}",
            "Type": random.choice(alert_types),
            "Severity": random.choice(["Low", "Medium", "High", "Critical"]),
            "Description": f"Detected suspicious activity in transaction pattern #{random.randint(100, 999)}",
            "Transaction Hash": hashlib.sha256(f"alert_tx_{i}_{int(time.time())}".encode()).hexdigest()[:16],
            "Amount": round(random.uniform(0.1, 100.0), 4),
            "Risk Score": random.randint(60, 100),  # Alerts typically have higher risk scores
            "Timestamp": datetime.now() - timedelta(minutes=random.randint(1, 720)),
            "Status": random.choice(["Open", "Investigating", "Resolved", "False Positive"]),
            "Assigned To": random.choice(["Auto", "Analyst 1", "Analyst 2", "Senior Analyst"]),
            "Source": random.choice(["ML Model", "Rule Engine", "Manual Review", "External API"])
        }
        alerts.append(alert)
    
    return pd.DataFrame(alerts)

def generate_hourly_data():
    """Generate hourly transaction and risk data for charts"""
    hours = list(range(24))
    current_hour = datetime.now().hour
    
    data = {
        'hours': hours,
        'transaction_counts': [random.randint(200, 800) for _ in hours],
        'risk_scores': [random.uniform(40, 80) for _ in hours],
        'alert_counts': [random.randint(0, 15) for _ in hours],
        'volume_btc': [random.uniform(50, 500) for _ in hours],
        'average_amount': [random.uniform(0.5, 5.0) for _ in hours]
    }
    
    # Make current hour data more realistic
    if current_hour < len(data['transaction_counts']):
        data['transaction_counts'][current_hour] = random.randint(600, 800)
        data['risk_scores'][current_hour] = random.uniform(60, 75)
    
    return data

def generate_weekly_data():
    """Generate weekly analytics data"""
    weeks = list(range(1, 13))  # 12 weeks
    
    return {
        'weeks': weeks,
        'high_risk': [random.randint(10, 50) for _ in weeks],
        'medium_risk': [random.randint(50, 100) for _ in weeks],
        'low_risk': [random.randint(200, 400) for _ in weeks],
        'total_volume': [random.randint(1000, 5000) for _ in weeks],
        'detection_rate': [random.uniform(85, 98) for _ in weeks]
    }

def generate_monthly_data():
    """Generate monthly fraud detection statistics"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    current_month = datetime.now().month
    
    data = {
        'months': months[:current_month],
        'detection_rate': [random.uniform(88, 96) for _ in range(current_month)],
        'false_positive_rate': [random.uniform(1, 5) for _ in range(current_month)],
        'total_transactions': [random.randint(50000, 200000) for _ in range(current_month)],
        'fraud_prevented': [random.randint(500, 2000) for _ in range(current_month)]
    }
    
    return data

def generate_risk_distribution():
    """Generate risk level distribution data"""
    return {
        'risk_levels': ['Low', 'Medium', 'High', 'Critical'],
        'counts': [45, 30, 20, 5],
        'colors': ['#059669', '#0052ff', '#ea580c', '#dc2626']
    }

def generate_system_metrics():
    """Generate system performance metrics"""
    return {
        'total_transactions_today': random.randint(10000, 15000),
        'fraud_alerts_today': random.randint(15, 35),
        'system_uptime': random.uniform(99.5, 99.99),
        'average_risk_score': random.uniform(45, 70),
        'processing_speed': random.randint(800, 1200),  # transactions per minute
        'false_positive_rate': random.uniform(2, 5),
        'detection_accuracy': random.uniform(92, 97),
        'active_users': random.randint(50, 150),
        'api_response_time': random.uniform(50, 200),  # milliseconds
        'database_connections': random.randint(10, 50)
    }

def generate_geographic_data():
    """Generate geographic transaction distribution"""
    countries = [
        'United States', 'Canada', 'United Kingdom', 'Germany', 
        'France', 'Japan', 'Australia', 'Singapore', 'Netherlands', 'Switzerland'
    ]
    
    data = []
    for country in countries:
        data.append({
            'country': country,
            'transaction_count': random.randint(100, 2000),
            'risk_score': random.uniform(30, 80),
            'total_volume': random.uniform(10, 500)  # BTC
        })
    
    return pd.DataFrame(data)

def generate_time_series_data(days=30):
    """Generate time series data for trends"""
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), end=datetime.now(), freq='D')
    
    data = {
        'date': dates,
        'transactions': [random.randint(1000, 5000) for _ in dates],
        'alerts': [random.randint(10, 100) for _ in dates],
        'risk_score': [random.uniform(40, 80) for _ in dates],
        'volume_btc': [random.uniform(100, 1000) for _ in dates],
        'new_addresses': [random.randint(50, 500) for _ in dates]
    }
    
    return pd.DataFrame(data)

def get_risk_level(risk_score):
    """Convert numeric risk score to risk level"""
    if risk_score >= 80:
        return "Critical"
    elif risk_score >= 60:
        return "High"
    elif risk_score >= 40:
        return "Medium"
    else:
        return "Low"

def format_currency(amount, currency="USD"):
    """Format currency amounts"""
    if currency == "BTC":
        return f"₿{amount:.8f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_hash(hash_string, length=8):
    """Format transaction hash for display"""
    if len(hash_string) > length * 2:
        return f"{hash_string[:length]}...{hash_string[-length:]}"
    return hash_string[:length * 2]