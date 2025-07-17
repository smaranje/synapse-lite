"""
Core module for Synapse-Lite application architecture
"""

__version__ = "2.0.0"
__author__ = "AI Assistant"

from .app_state import AppState
from .theme_manager import ThemeManager
from .navigation import NavigationManager

__all__ = [
    "AppState",
    "ThemeManager", 
    "NavigationManager"
]