"""
Data generation utilities for the Synapse-Lite Fraud Detection Dashboard
"""

import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List

def generate_transaction_hash() -> str:
    """Generate a realistic Bitcoin transaction hash"""
    return hashlib.sha256(str(random.random()).encode()).hexdigest()

def generate_bitcoin_address() -> str:
    """Generate a realistic Bitcoin address"""
    prefixes = ['1', '3', 'bc1']
    prefix = random.choice(prefixes)
    chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    return prefix + ''.join(random.choices(chars, k=33))

def calculate_risk_level(ml_score: float, is_smurfing: bool) -> str:
    """Calculate risk level based on ML score and smurfing flag"""
    if is_smurfing or ml_score >= 0.8:
        return "Critical"
    elif ml_score >= 0.6:
        return "High"
    elif ml_score >= 0.4:
        return "Medium"
    else:
        return "Low"

def generate_dummy_transactions(n: int = 100) -> List[Dict]:
    """Generate dummy transaction data"""
    transactions = []
    base_time = datetime.now() - timedelta(hours=24)
    
    for i in range(n):
        ml_score = random.random()
        is_smurfing = random.random() > 0.85
        
        # Generate more realistic transaction patterns
        if is_smurfing:
            # Smurfing transactions typically have many outputs
            num_outputs = random.randint(10, 50)
            total_value = random.uniform(0.1, 2.0)
        else:
            num_outputs = random.randint(1, 5)
            total_value = random.uniform(0.001, 10.0)
        
        transaction = {
            'hash': generate_transaction_hash(),
            'timestamp': base_time + timedelta(minutes=i*15),
            'total_input_value': total_value,
            'total_output_value': total_value * 0.999,  # Small fee
            'fee': total_value * 0.001,
            'size': random.randint(200, 2000),
            'num_inputs': random.randint(1, 10),
            'num_outputs': num_outputs,
            'input_addresses': [generate_bitcoin_address() for _ in range(random.randint(1, 5))],
            'output_addresses': [generate_bitcoin_address() for _ in range(num_outputs)],
            'ml_score': ml_score,
            'is_smurfing_rule': is_smurfing,
            'risk_level': calculate_risk_level(ml_score, is_smurfing),
            'total_value_btc': total_value,
            'total_value_usd': total_value * 45000  # Approximate BTC/USD rate
        }
        transactions.append(transaction)
    
    return transactions

def generate_dummy_alerts(transactions: List[Dict]) -> List[Dict]:
    """Generate alerts from high-risk transactions"""
    alerts = []
    alert_id = 1000
    
    for tx in transactions:
        if tx['risk_level'] in ['Critical', 'High']:
            alert = {
                'alert_id': f"ALT-{alert_id}",
                'transaction_hash': tx['hash'],
                'risk_level': tx['risk_level'],
                'timestamp': tx['timestamp'],
                'ml_score': tx['ml_score'],
                'is_smurfing': tx['is_smurfing_rule'],
                'total_value_btc': tx['total_value_btc'],
                'total_value_usd': tx['total_value_usd'],
                'num_inputs': tx['num_inputs'],
                'num_outputs': tx['num_outputs'],
                'fee': tx['fee'],
                'description': get_alert_description(tx),
                'status': 'Open'
            }
            alerts.append(alert)
            alert_id += 1
    
    return alerts

def get_alert_description(transaction: Dict) -> str:
    """Generate alert description based on transaction characteristics"""
    descriptions = []
    
    if transaction['is_smurfing_rule']:
        descriptions.append("Smurfing pattern detected")
    
    if transaction['ml_score'] >= 0.8:
        descriptions.append("Very high ML fraud score")
    elif transaction['ml_score'] >= 0.6:
        descriptions.append("High ML fraud score")
    
    if transaction['num_outputs'] > 20:
        descriptions.append(f"Unusual number of outputs ({transaction['num_outputs']})")
    
    if transaction['total_value_btc'] > 5:
        descriptions.append("Large transaction value")
    
    return "; ".join(descriptions) if descriptions else "Suspicious activity detected"

def generate_sar(alert_data: Dict) -> str:
    """Generate a Suspicious Activity Report"""
    return f"""SUSPICIOUS ACTIVITY REPORT (SAR)
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ALERT ID: {alert_data['alert_id']}
Transaction Hash: {alert_data['transaction_hash']}
Risk Level: {alert_data['risk_level']}

EXECUTIVE SUMMARY:
This transaction has been flagged due to {alert_data['description'].lower()}. The transaction exhibits characteristics consistent with potential money laundering activity and warrants immediate investigation.

TRANSACTION DETAILS:
- Date/Time: {alert_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
- Transaction Value: {alert_data['total_value_btc']:.6f} BTC (${alert_data['total_value_usd']:,.2f} USD)
- Number of Inputs: {alert_data['num_inputs']}
- Number of Outputs: {alert_data['num_outputs']}
- Transaction Fee: {alert_data['fee']:.8f} BTC
- ML Fraud Score: {alert_data['ml_score']:.2%}
- Smurfing Detection: {'POSITIVE' if alert_data['is_smurfing'] else 'NEGATIVE'}

SUSPICIOUS INDICATORS:
1. {alert_data['description']}
2. Transaction structure suggests attempt to obscure fund origin/destination
3. Pattern consistent with known money laundering typologies

RECOMMENDATION:
Based on the automated analysis, this transaction exhibits multiple red flags for potential money laundering activity. Recommended actions:
1. Immediate KYC verification of all involved addresses
2. Extended transaction pattern analysis (30-day lookback)
3. Cross-reference with OFAC and other sanctions lists
4. Consider filing SAR with FinCEN within regulatory timeframe

COMPLIANCE OFFICER NOTES:
[To be completed by reviewing officer]

This report is generated automatically by the Synapse-Lite Fraud Detection System and should be reviewed by a qualified compliance officer before submission to regulatory authorities."""