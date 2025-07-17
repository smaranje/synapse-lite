"""
Mock Data Generator for Synapse-Lite
Generates realistic sample data for development and demo purposes
"""

import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np

class MockDataGenerator:
    """Generates mock data for the fraud detection system"""
    
    def __init__(self):
        self.btc_usd_rate = 65000
        self.risk_patterns = [
            "Multiple small transactions",
            "Suspicious wallet clustering",
            "High-frequency trading pattern",
            "Geographic anomaly",
            "Velocity threshold exceeded",
            "Round amount pattern",
            "Mixing service detected",
            "Known blacklisted address"
        ]
        
        self.countries = [
            "United States", "China", "Germany", "United Kingdom", "Japan",
            "Canada", "France", "Australia", "Netherlands", "Singapore",
            "South Korea", "Russia", "Brazil", "India", "Switzerland"
        ]
        
        self.wallet_types = [
            "Personal Wallet", "Exchange Hot Wallet", "Exchange Cold Storage",
            "Mining Pool", "DeFi Protocol", "Institutional Custody",
            "Unknown", "Suspicious Entity"
        ]
    
    def _generate_hash(self, prefix: str = "tx") -> str:
        """Generate a realistic transaction hash"""
        random_data = f"{prefix}_{random.randint(100000, 999999)}_{datetime.now().timestamp()}"
        return hashlib.sha256(random_data.encode()).hexdigest()
    
    def _generate_address(self) -> str:
        """Generate a Bitcoin address"""
        prefixes = ['1', '3', 'bc1']
        prefix = random.choice(prefixes)
        if prefix == 'bc1':
            length = random.randint(39, 59)
        else:
            length = random.randint(26, 35)
        
        chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
        address = prefix + ''.join(random.choice(chars) for _ in range(length - len(prefix)))
        return address
    
    def generate_transactions(self, count: int = 100) -> List[Dict]:
        """Generate mock transaction data"""
        transactions = []
        
        for i in range(count):
            timestamp = datetime.now() - timedelta(minutes=random.randint(0, 1440))
            amount_btc = round(random.uniform(0.001, 50.0), 8)
            amount_usd = round(amount_btc * self.btc_usd_rate, 2)
            risk_score = random.randint(1, 100)
            
            # Determine status based on risk score
            if risk_score > 90:
                status = "flagged"
            elif risk_score > 70:
                status = "review"
            else:
                status = random.choice(["confirmed", "confirmed", "confirmed", "pending"])
            
            transaction = {
                'id': f"tx_{i+1:06d}",
                'hash': self._generate_hash(),
                'timestamp': timestamp.isoformat(),
                'amount_btc': amount_btc,
                'amount_usd': amount_usd,
                'fee_btc': round(random.uniform(0.00001, 0.001), 8),
                'fee_usd': round(random.uniform(0.65, 65), 2),
                'from_address': self._generate_address(),
                'to_address': self._generate_address(),
                'confirmations': random.randint(0, 6) if status != "confirmed" else random.randint(6, 100),
                'block_height': random.randint(800000, 810000),
                'risk_score': risk_score,
                'status': status,
                'size_bytes': random.randint(250, 2000),
                'input_count': random.randint(1, 5),
                'output_count': random.randint(1, 8),
                'country': random.choice(self.countries),
                'wallet_type': random.choice(self.wallet_types),
                'risk_factors': random.sample(self.risk_patterns, random.randint(0, 3)) if risk_score > 50 else []
            }
            
            transactions.append(transaction)
        
        return sorted(transactions, key=lambda x: x['timestamp'], reverse=True)
    
    def generate_alerts(self, count: int = 50) -> List[Dict]:
        """Generate mock fraud alerts"""
        alerts = []
        alert_types = [
            "Suspicious Pattern Detection",
            "High-Risk Transaction",
            "Velocity Threshold Exceeded",
            "Geographic Anomaly",
            "Known Bad Actor",
            "Mixing Service Detection",
            "Smurfing Activity",
            "Round Amount Pattern",
            "Wallet Clustering",
            "AML Compliance Flag"
        ]
        
        severities = ["low", "medium", "high", "critical"]
        statuses = ["active", "investigating", "resolved", "false_positive"]
        
        for i in range(count):
            severity = random.choice(severities)
            timestamp = datetime.now() - timedelta(hours=random.randint(0, 72))
            
            alert = {
                'id': f"ALT-{random.randint(10000, 99999)}",
                'type': random.choice(alert_types),
                'severity': severity,
                'status': random.choice(statuses),
                'timestamp': timestamp.isoformat(),
                'description': f"Automated detection of {random.choice(alert_types).lower()}",
                'risk_score': random.randint(70, 100) if severity in ['high', 'critical'] else random.randint(30, 80),
                'affected_addresses': [self._generate_address() for _ in range(random.randint(1, 5))],
                'transaction_count': random.randint(1, 50),
                'total_amount_usd': round(random.uniform(1000, 1000000), 2),
                'country': random.choice(self.countries),
                'investigation_notes': f"Alert generated by ML model with {random.randint(85, 99)}% confidence",
                'assigned_to': random.choice(["System", "Analyst A", "Analyst B", "Senior Investigator"]),
                'created_by': "AI Detection System",
                'last_updated': timestamp.isoformat()
            }
            
            alerts.append(alert)
        
        return sorted(alerts, key=lambda x: x['timestamp'], reverse=True)
    
    def generate_system_metrics(self) -> Dict[str, Any]:
        """Generate system performance metrics"""
        return {
            'transactions_processed_today': random.randint(15000, 45000),
            'alerts_generated_today': random.randint(50, 200),
            'system_uptime_hours': round(random.uniform(48, 720), 1),
            'avg_processing_time_ms': round(random.uniform(15, 45), 2),
            'avg_risk_score': round(random.uniform(25, 40), 1),
            'detection_accuracy': round(random.uniform(94, 99), 2),
            'false_positive_rate': round(random.uniform(1, 5), 2),
            'total_volume_today_usd': round(random.uniform(50000000, 200000000), 2),
            'high_risk_transactions': random.randint(100, 500),
            'blocked_transactions': random.randint(10, 50),
            'api_requests_today': random.randint(10000, 50000),
            'active_investigations': random.randint(5, 25),
            'resolved_cases_today': random.randint(2, 10)
        }
    
    def generate_hourly_volume_data(self) -> Dict[str, Any]:
        """Generate hourly transaction volume data for last 24 hours"""
        hours = []
        volumes = []
        transaction_counts = []
        
        for i in range(24):
            hour = datetime.now() - timedelta(hours=23-i)
            hours.append(hour.strftime('%H:00'))
            
            # Simulate daily patterns (higher during business hours)
            base_volume = 1000000
            hour_multiplier = 1.0
            if 9 <= hour.hour <= 17:
                hour_multiplier = 1.5
            elif 18 <= hour.hour <= 22:
                hour_multiplier = 1.2
            elif 0 <= hour.hour <= 6:
                hour_multiplier = 0.6
            
            volume = base_volume * hour_multiplier * random.uniform(0.7, 1.3)
            count = int(volume / random.uniform(800, 1200))
            
            volumes.append(round(volume, 2))
            transaction_counts.append(count)
        
        return {
            'hours': hours,
            'volumes': volumes,
            'transaction_counts': transaction_counts
        }
    
    def generate_daily_volume_data(self, days: int) -> Dict[str, Any]:
        """Generate daily volume data"""
        dates = []
        volumes = []
        transaction_counts = []
        
        for i in range(days):
            date = datetime.now().date() - timedelta(days=days-1-i)
            dates.append(date.strftime('%Y-%m-%d'))
            
            # Weekend pattern (lower volume)
            is_weekend = date.weekday() >= 5
            base_volume = 15000000 if not is_weekend else 8000000
            
            volume = base_volume * random.uniform(0.8, 1.2)
            count = int(volume / random.uniform(900, 1100))
            
            volumes.append(round(volume, 2))
            transaction_counts.append(count)
        
        return {
            'dates': dates,
            'volumes': volumes,
            'transaction_counts': transaction_counts
        }
    
    def generate_risk_analytics(self) -> Dict[str, Any]:
        """Generate risk analytics data"""
        return {
            'risk_distribution': {
                'low': random.randint(70, 85),
                'medium': random.randint(10, 20),
                'high': random.randint(3, 8),
                'critical': random.randint(1, 3)
            },
            'detection_methods': {
                'ML Model': random.randint(40, 60),
                'Rule Engine': random.randint(20, 35),
                'Blacklist': random.randint(5, 15),
                'Manual Review': random.randint(5, 10)
            },
            'top_risk_countries': [
                {'country': 'Unknown', 'risk_score': random.randint(80, 95)},
                {'country': 'Country A', 'risk_score': random.randint(70, 85)},
                {'country': 'Country B', 'risk_score': random.randint(65, 80)},
                {'country': 'Country C', 'risk_score': random.randint(60, 75)},
                {'country': 'Country D', 'risk_score': random.randint(55, 70)}
            ],
            'trend_data': {
                'dates': [(datetime.now().date() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7, 0, -1)],
                'risk_scores': [round(random.uniform(20, 45), 1) for _ in range(7)]
            }
        }
    
    def generate_geographic_data(self) -> List[Dict]:
        """Generate geographic transaction data"""
        geo_data = []
        
        for country in self.countries:
            data = {
                'country': country,
                'transaction_count': random.randint(100, 5000),
                'total_volume_usd': round(random.uniform(100000, 10000000), 2),
                'avg_risk_score': round(random.uniform(15, 85), 1),
                'high_risk_count': random.randint(5, 100),
                'latitude': round(random.uniform(-60, 70), 6),
                'longitude': round(random.uniform(-180, 180), 6)
            }
            geo_data.append(data)
        
        return geo_data
    
    def generate_investigation_cases(self) -> List[Dict]:
        """Generate investigation cases"""
        cases = []
        case_types = [
            "Money Laundering Investigation",
            "Terrorist Financing Case",
            "Exchange Hack Analysis",
            "Ransomware Payment Tracking",
            "Drug Transaction Network",
            "Fraud Ring Investigation",
            "Mixer Service Analysis",
            "Compliance Violation"
        ]
        
        for i in range(15):
            created_date = datetime.now() - timedelta(days=random.randint(0, 90))
            status = random.choice(["open", "investigating", "pending_review", "closed", "escalated"])
            
            case = {
                'id': f"CASE-{random.randint(10000, 99999)}",
                'title': random.choice(case_types),
                'description': f"Investigation into suspicious Bitcoin transaction patterns",
                'status': status,
                'priority': random.choice(["low", "medium", "high", "urgent"]),
                'created_at': created_date.isoformat(),
                'assigned_to': random.choice(["Analyst A", "Analyst B", "Senior Investigator", "Team Lead"]),
                'estimated_amount_usd': round(random.uniform(10000, 5000000), 2),
                'related_addresses': [self._generate_address() for _ in range(random.randint(3, 15))],
                'related_transactions': random.randint(5, 100),
                'evidence_count': random.randint(0, 25),
                'last_activity': (created_date + timedelta(days=random.randint(0, 10))).isoformat(),
                'tags': random.sample(['aml', 'high-risk', 'exchange', 'mixer', 'darknet', 'ransomware'], random.randint(1, 3))
            }
            
            cases.append(case)
        
        return sorted(cases, key=lambda x: x['created_at'], reverse=True)
    
    def generate_daily_summary(self) -> Dict[str, Any]:
        """Generate daily summary report"""
        return {
            'date': datetime.now().date().isoformat(),
            'total_transactions': random.randint(15000, 35000),
            'total_volume_usd': round(random.uniform(50000000, 150000000), 2),
            'alerts_generated': random.randint(50, 150),
            'high_risk_alerts': random.randint(5, 25),
            'investigations_opened': random.randint(2, 8),
            'investigations_closed': random.randint(1, 5),
            'blocked_amount_usd': round(random.uniform(100000, 2000000), 2),
            'processing_accuracy': round(random.uniform(96, 99.5), 2),
            'system_uptime': round(random.uniform(99, 100), 3)
        }
    
    def generate_weekly_summary(self) -> Dict[str, Any]:
        """Generate weekly summary report"""
        return {
            'week_ending': datetime.now().date().isoformat(),
            'total_transactions': random.randint(100000, 250000),
            'total_volume_usd': round(random.uniform(400000000, 1000000000), 2),
            'alerts_generated': random.randint(300, 800),
            'resolution_rate': round(random.uniform(85, 95), 1),
            'false_positive_rate': round(random.uniform(2, 8), 1),
            'avg_investigation_time_hours': round(random.uniform(24, 72), 1),
            'top_risk_patterns': random.sample(self.risk_patterns, 5)
        }
    
    def generate_monthly_summary(self) -> Dict[str, Any]:
        """Generate monthly summary report"""
        return {
            'month': datetime.now().strftime('%Y-%m'),
            'total_transactions': random.randint(400000, 1000000),
            'total_volume_usd': round(random.uniform(2000000000, 5000000000), 2),
            'compliance_score': round(random.uniform(92, 98), 1),
            'regulatory_reports_filed': random.randint(50, 200),
            'cost_savings_usd': round(random.uniform(500000, 2000000), 2),
            'model_accuracy_improvement': round(random.uniform(1, 5), 1)
        }
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report"""
        return {
            'report_date': datetime.now().date().isoformat(),
            'suspicious_activity_reports': random.randint(20, 80),
            'currency_transaction_reports': random.randint(100, 300),
            'kyc_checks_performed': random.randint(500, 1500),
            'aml_flags': random.randint(50, 150),
            'regulatory_queries': random.randint(5, 20),
            'audit_findings': random.randint(0, 5),
            'compliance_training_completed': random.randint(15, 50)
        }