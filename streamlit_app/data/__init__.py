"""
Data layer for Synapse-Lite application
Handles data generation, processing, and services
"""

from .data_service import DataService
from .mock_data_generator import MockDataGenerator

__all__ = [
    "DataService",
    "MockDataGenerator"
]