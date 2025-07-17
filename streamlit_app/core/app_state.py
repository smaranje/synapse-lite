"""
Application State Management for Synapse-Lite
Centralized state management for the fraud detection system
"""

import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading
import time

class AppState:
    """Centralized application state management"""
    
    def __init__(self):
        self._initialized = False
        self._last_refresh = None
        self._refresh_interval = 30  # seconds
        self._settings = self._load_default_settings()
        
    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default application settings"""
        return {
            'theme': 'dark',
            'auto_refresh': True,
            'refresh_interval': 30,
            'show_notifications': True,
            'debug_mode': False,
            'api_timeout': 10,
            'max_transactions_display': 1000,
            'alert_threshold': 80,
            'enable_sound_alerts': False,
            'currency': 'USD',
            'timezone': 'UTC',
            'data_retention_days': 30,
            'enable_real_time': True,
            'chart_animation': True,
            'compact_view': False
        }
    
    def initialize(self):
        """Initialize application state"""
        if not self._initialized:
            # Initialize session state variables
            if 'current_page' not in st.session_state:
                st.session_state.current_page = 'overview'
            
            if 'user_settings' not in st.session_state:
                st.session_state.user_settings = self._settings.copy()
            
            if 'alerts_data' not in st.session_state:
                st.session_state.alerts_data = []
            
            if 'transactions_data' not in st.session_state:
                st.session_state.transactions_data = []
            
            if 'system_metrics' not in st.session_state:
                st.session_state.system_metrics = {}
            
            if 'investigation_cases' not in st.session_state:
                st.session_state.investigation_cases = []
            
            if 'data_last_updated' not in st.session_state:
                st.session_state.data_last_updated = None
            
            self._initialized = True
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a user setting value"""
        return st.session_state.get('user_settings', {}).get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set a user setting value"""
        if 'user_settings' not in st.session_state:
            st.session_state.user_settings = self._settings.copy()
        st.session_state.user_settings[key] = value
    
    def get_current_page(self) -> str:
        """Get the current page"""
        return st.session_state.get('current_page', 'overview')
    
    def set_current_page(self, page: str):
        """Set the current page"""
        st.session_state.current_page = page
    
    def should_refresh_data(self) -> bool:
        """Check if data should be refreshed"""
        if not self.get_setting('auto_refresh', True):
            return False
        
        if not st.session_state.get('data_last_updated'):
            return True
            
        last_update = st.session_state.data_last_updated
        if isinstance(last_update, str):
            last_update = datetime.fromisoformat(last_update)
        
        time_diff = datetime.now() - last_update
        return time_diff.total_seconds() >= self.get_setting('refresh_interval', 30)
    
    def refresh_data(self):
        """Refresh application data"""
        from data.data_service import DataService
        
        try:
            data_service = DataService()
            
            # Update transactions data
            st.session_state.transactions_data = data_service.get_recent_transactions()
            
            # Update alerts data
            st.session_state.alerts_data = data_service.get_active_alerts()
            
            # Update system metrics
            st.session_state.system_metrics = data_service.get_system_metrics()
            
            # Update timestamp
            st.session_state.data_last_updated = datetime.now()
            
        except Exception as e:
            st.error(f"Failed to refresh data: {str(e)}")
    
    def get_transactions_data(self) -> list:
        """Get transactions data"""
        return st.session_state.get('transactions_data', [])
    
    def get_alerts_data(self) -> list:
        """Get alerts data"""
        return st.session_state.get('alerts_data', [])
    
    def get_system_metrics(self) -> dict:
        """Get system metrics"""
        return st.session_state.get('system_metrics', {})
    
    def add_alert(self, alert: dict):
        """Add a new alert"""
        alerts = st.session_state.get('alerts_data', [])
        alert['id'] = len(alerts) + 1
        alert['timestamp'] = datetime.now().isoformat()
        alerts.insert(0, alert)  # Add to beginning
        st.session_state.alerts_data = alerts
    
    def update_alert_status(self, alert_id: int, status: str):
        """Update alert status"""
        alerts = st.session_state.get('alerts_data', [])
        for alert in alerts:
            if alert.get('id') == alert_id:
                alert['status'] = status
                alert['updated_at'] = datetime.now().isoformat()
                break
        st.session_state.alerts_data = alerts
    
    def get_investigation_cases(self) -> list:
        """Get investigation cases"""
        return st.session_state.get('investigation_cases', [])
    
    def add_investigation_case(self, case: dict):
        """Add a new investigation case"""
        cases = st.session_state.get('investigation_cases', [])
        case['id'] = len(cases) + 1
        case['created_at'] = datetime.now().isoformat()
        case['status'] = 'open'
        cases.insert(0, case)
        st.session_state.investigation_cases = cases
    
    def get_data_last_updated(self) -> Optional[datetime]:
        """Get when data was last updated"""
        last_updated = st.session_state.get('data_last_updated')
        if isinstance(last_updated, str):
            return datetime.fromisoformat(last_updated)
        return last_updated
    
    def export_settings(self) -> str:
        """Export user settings as JSON"""
        return json.dumps(st.session_state.get('user_settings', {}), indent=2)
    
    def import_settings(self, settings_json: str):
        """Import user settings from JSON"""
        try:
            settings = json.loads(settings_json)
            st.session_state.user_settings = {**self._settings, **settings}
            return True
        except Exception:
            return False
    
    def reset_settings(self):
        """Reset settings to defaults"""
        st.session_state.user_settings = self._settings.copy()
    
    def get_summary_stats(self) -> dict:
        """Get summary statistics"""
        transactions = self.get_transactions_data()
        alerts = self.get_alerts_data()
        metrics = self.get_system_metrics()
        
        return {
            'total_transactions_today': len([t for t in transactions if self._is_today(t.get('timestamp'))]),
            'active_alerts': len([a for a in alerts if a.get('status') == 'active']),
            'total_volume_today': sum([t.get('amount_usd', 0) for t in transactions if self._is_today(t.get('timestamp'))]),
            'avg_risk_score': metrics.get('avg_risk_score', 0),
            'system_uptime': metrics.get('uptime_hours', 0),
            'processing_rate': metrics.get('transactions_per_second', 0)
        }
    
    def _is_today(self, timestamp_str: str) -> bool:
        """Check if timestamp is from today"""
        if not timestamp_str:
            return False
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return timestamp.date() == datetime.now().date()
        except:
            return False