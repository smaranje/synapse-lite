"""
Data Service for Synapse-Lite
Centralized data access and management
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
import numpy as np
from .mock_data_generator import MockDataGenerator

class DataService:
    """Centralized data service for the application"""
    
    def __init__(self):
        self.mock_generator = MockDataGenerator()
        self._cache = {}
        self._cache_timeout = 30  # seconds
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._cache:
            return False
        
        cache_time = self._cache[key].get('timestamp', datetime.min)
        return (datetime.now() - cache_time).total_seconds() < self._cache_timeout
    
    def _get_cached_data(self, key: str) -> Any:
        """Get data from cache"""
        if self._is_cache_valid(key):
            return self._cache[key]['data']
        return None
    
    def _set_cache(self, key: str, data: Any):
        """Set data in cache"""
        self._cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def get_recent_transactions(self, limit: int = 100) -> List[Dict]:
        """Get recent transactions"""
        cache_key = f"transactions_{limit}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        transactions = self.mock_generator.generate_transactions(limit)
        self._set_cache(cache_key, transactions)
        return transactions
    
    def get_active_alerts(self, limit: int = 50) -> List[Dict]:
        """Get active fraud alerts"""
        cache_key = f"alerts_{limit}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        alerts = self.mock_generator.generate_alerts(limit)
        self._set_cache(cache_key, alerts)
        return alerts
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        cache_key = "system_metrics"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        metrics = self.mock_generator.generate_system_metrics()
        self._set_cache(cache_key, metrics)
        return metrics
    
    def get_transaction_volume_data(self, period: str = '24h') -> Dict[str, Any]:
        """Get transaction volume data for charts"""
        cache_key = f"volume_data_{period}"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        if period == '24h':
            data = self.mock_generator.generate_hourly_volume_data()
        elif period == '7d':
            data = self.mock_generator.generate_daily_volume_data(7)
        elif period == '30d':
            data = self.mock_generator.generate_daily_volume_data(30)
        else:
            data = self.mock_generator.generate_hourly_volume_data()
        
        self._set_cache(cache_key, data)
        return data
    
    def get_risk_analytics(self) -> Dict[str, Any]:
        """Get risk analytics data"""
        cache_key = "risk_analytics"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        analytics = self.mock_generator.generate_risk_analytics()
        self._set_cache(cache_key, analytics)
        return analytics
    
    def get_geographic_data(self) -> List[Dict]:
        """Get geographic transaction data"""
        cache_key = "geographic_data"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        geo_data = self.mock_generator.generate_geographic_data()
        self._set_cache(cache_key, geo_data)
        return geo_data
    
    def search_transactions(self, 
                          search_term: str = "",
                          risk_threshold: float = 0,
                          date_from: Optional[datetime] = None,
                          date_to: Optional[datetime] = None,
                          status_filter: str = "all") -> List[Dict]:
        """Search transactions with filters"""
        transactions = self.get_recent_transactions(1000)
        
        filtered = []
        for txn in transactions:
            # Apply filters
            if search_term and search_term.lower() not in str(txn.get('hash', '')).lower():
                continue
            
            if txn.get('risk_score', 0) < risk_threshold:
                continue
            
            if date_from and datetime.fromisoformat(txn.get('timestamp', '')) < date_from:
                continue
            
            if date_to and datetime.fromisoformat(txn.get('timestamp', '')) > date_to:
                continue
            
            if status_filter != "all" and txn.get('status', '').lower() != status_filter.lower():
                continue
            
            filtered.append(txn)
        
        return filtered[:100]  # Limit results
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        alerts = self.get_active_alerts(200)
        
        total_alerts = len(alerts)
        high_risk = len([a for a in alerts if a.get('severity') == 'high'])
        medium_risk = len([a for a in alerts if a.get('severity') == 'medium'])
        low_risk = len([a for a in alerts if a.get('severity') == 'low'])
        
        resolved = len([a for a in alerts if a.get('status') == 'resolved'])
        pending = len([a for a in alerts if a.get('status') == 'pending'])
        active = len([a for a in alerts if a.get('status') == 'active'])
        
        return {
            'total_alerts': total_alerts,
            'high_risk_alerts': high_risk,
            'medium_risk_alerts': medium_risk,
            'low_risk_alerts': low_risk,
            'resolved_alerts': resolved,
            'pending_alerts': pending,
            'active_alerts': active,
            'resolution_rate': (resolved / total_alerts * 100) if total_alerts > 0 else 0
        }
    
    def get_transaction_statistics(self) -> Dict[str, Any]:
        """Get transaction statistics"""
        transactions = self.get_recent_transactions(1000)
        
        total_count = len(transactions)
        total_volume = sum([t.get('amount_usd', 0) for t in transactions])
        avg_amount = total_volume / total_count if total_count > 0 else 0
        
        high_risk_count = len([t for t in transactions if t.get('risk_score', 0) > 80])
        flagged_count = len([t for t in transactions if t.get('status') == 'flagged'])
        
        return {
            'total_transactions': total_count,
            'total_volume_usd': total_volume,
            'average_transaction_usd': avg_amount,
            'high_risk_transactions': high_risk_count,
            'flagged_transactions': flagged_count,
            'high_risk_percentage': (high_risk_count / total_count * 100) if total_count > 0 else 0
        }
    
    def get_realtime_data(self) -> Dict[str, Any]:
        """Get real-time monitoring data"""
        return {
            'transactions_per_second': round(random.uniform(5.0, 25.0), 1),
            'current_load': random.randint(60, 95),
            'active_connections': random.randint(150, 500),
            'processing_latency_ms': round(random.uniform(10.0, 50.0), 1),
            'queue_size': random.randint(0, 100),
            'success_rate': round(random.uniform(95.0, 99.9), 2),
            'current_risk_level': random.choice(['low', 'medium', 'high']),
            'anomaly_detection_active': True,
            'ai_model_accuracy': round(random.uniform(92.0, 98.5), 1)
        }
    
    def get_investigation_cases(self) -> List[Dict]:
        """Get investigation cases"""
        cache_key = "investigation_cases"
        cached_data = self._get_cached_data(cache_key)
        
        if cached_data is not None:
            return cached_data
        
        cases = self.mock_generator.generate_investigation_cases()
        self._set_cache(cache_key, cases)
        return cases
    
    def create_investigation_case(self, case_data: Dict) -> Dict:
        """Create a new investigation case"""
        case = {
            'id': f"CASE-{random.randint(10000, 99999)}",
            'title': case_data.get('title', 'New Investigation'),
            'description': case_data.get('description', ''),
            'severity': case_data.get('severity', 'medium'),
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'assigned_to': case_data.get('assigned_to', 'System'),
            'related_transactions': case_data.get('related_transactions', []),
            'evidence': [],
            'notes': []
        }
        return case
    
    def get_reports_data(self) -> Dict[str, Any]:
        """Get reports and analytics data"""
        return {
            'daily_summary': self.mock_generator.generate_daily_summary(),
            'weekly_summary': self.mock_generator.generate_weekly_summary(),
            'monthly_summary': self.mock_generator.generate_monthly_summary(),
            'compliance_report': self.mock_generator.generate_compliance_report()
        }
    
    def export_data(self, data_type: str, format: str = 'csv') -> str:
        """Export data in various formats"""
        if data_type == 'transactions':
            data = self.get_recent_transactions(1000)
        elif data_type == 'alerts':
            data = self.get_active_alerts(500)
        elif data_type == 'investigations':
            data = self.get_investigation_cases()
        else:
            raise ValueError(f"Unknown data type: {data_type}")
        
        if format == 'csv':
            df = pd.DataFrame(data)
            return df.to_csv(index=False)
        elif format == 'json':
            import json
            return json.dumps(data, indent=2, default=str)
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get application performance metrics"""
        return {
            'cache_hit_rate': round(random.uniform(75.0, 95.0), 1),
            'data_freshness_score': round(random.uniform(85.0, 99.0), 1),
            'api_response_time_ms': round(random.uniform(50.0, 200.0), 1),
            'database_connections': random.randint(5, 20),
            'memory_usage_mb': round(random.uniform(150.0, 500.0), 1),
            'cpu_usage_percent': round(random.uniform(15.0, 80.0), 1)
        }