"""
Pages module for Synapse-Lite
Contains all application pages and their implementations
"""

from .overview import OverviewPage
from .realtime import RealtimePage
from .transactions import TransactionsPage
from .alerts import AlertsPage
from .analytics import AnalyticsPage
from .investigations import InvestigationsPage
from .reports import ReportsPage
from .settings import SettingsPage

__all__ = [
    "OverviewPage",
    "RealtimePage",
    "TransactionsPage", 
    "AlertsPage",
    "AnalyticsPage",
    "InvestigationsPage",
    "ReportsPage",
    "SettingsPage"
]