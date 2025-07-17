"""
Navigation Manager for Synapse-Lite
Handles page routing and navigation state management
"""

from typing import Dict, List, Optional
import streamlit as st

class NavigationManager:
    """Manages application navigation and routing"""
    
    def __init__(self):
        self.pages = self._initialize_pages()
    
    def _initialize_pages(self) -> Dict[str, Dict]:
        """Initialize page configuration"""
        return {
            'overview': {
                'title': 'Overview',
                'icon': '🏠',
                'description': 'System overview and key metrics',
                'path': '/overview',
                'category': 'main'
            },
            'realtime': {
                'title': 'Real-time Monitor',
                'icon': '📊',
                'description': 'Live transaction monitoring',
                'path': '/realtime',
                'category': 'main'
            },
            'transactions': {
                'title': 'Transactions',
                'icon': '💰',
                'description': 'Transaction analysis and search',
                'path': '/transactions',
                'category': 'analysis'
            },
            'alerts': {
                'title': 'Alerts',
                'icon': '🚨',
                'description': 'Fraud alerts and notifications',
                'path': '/alerts',
                'category': 'analysis'
            },
            'analytics': {
                'title': 'Analytics',
                'icon': '📈',
                'description': 'Advanced analytics and trends',
                'path': '/analytics',
                'category': 'analysis'
            },
            'investigations': {
                'title': 'Investigations',
                'icon': '🔍',
                'description': 'Case management and investigation tools',
                'path': '/investigations',
                'category': 'investigation'
            },
            'reports': {
                'title': 'Reports',
                'icon': '📋',
                'description': 'Generate and view reports',
                'path': '/reports',
                'category': 'investigation'
            },
            'settings': {
                'title': 'Settings',
                'icon': '⚙️',
                'description': 'Application settings and configuration',
                'path': '/settings',
                'category': 'admin'
            }
        }
    
    def get_pages_by_category(self, category: str) -> Dict[str, Dict]:
        """Get pages filtered by category"""
        return {
            key: page for key, page in self.pages.items() 
            if page.get('category') == category
        }
    
    def get_page_info(self, page_key: str) -> Optional[Dict]:
        """Get information about a specific page"""
        return self.pages.get(page_key)
    
    def get_all_pages(self) -> Dict[str, Dict]:
        """Get all pages"""
        return self.pages
    
    def get_page_categories(self) -> List[str]:
        """Get all page categories"""
        categories = set()
        for page in self.pages.values():
            categories.add(page.get('category', 'main'))
        return sorted(list(categories))
    
    def navigate_to(self, page_key: str):
        """Navigate to a specific page"""
        if page_key in self.pages:
            st.session_state.current_page = page_key
    
    def get_current_page(self) -> str:
        """Get the current page key"""
        return st.session_state.get('current_page', 'overview')
    
    def get_current_page_info(self) -> Dict:
        """Get information about the current page"""
        current = self.get_current_page()
        return self.get_page_info(current) or self.pages['overview']
    
    def get_breadcrumbs(self) -> List[Dict]:
        """Get breadcrumb navigation for current page"""
        current_page = self.get_current_page_info()
        category = current_page.get('category', 'main')
        
        breadcrumbs = [
            {'title': 'Home', 'key': 'overview'},
        ]
        
        if category != 'main':
            breadcrumbs.append({
                'title': category.title(),
                'key': None  # Category doesn't have a direct page
            })
        
        if self.get_current_page() != 'overview':
            breadcrumbs.append({
                'title': current_page.get('title', 'Unknown'),
                'key': self.get_current_page()
            })
        
        return breadcrumbs
    
    def get_navigation_menu(self) -> Dict[str, List[Dict]]:
        """Get organized navigation menu structure"""
        menu = {}
        
        for page_key, page_info in self.pages.items():
            category = page_info.get('category', 'main')
            
            if category not in menu:
                menu[category] = []
            
            menu[category].append({
                'key': page_key,
                'title': page_info.get('title'),
                'icon': page_info.get('icon'),
                'description': page_info.get('description')
            })
        
        return menu
    
    def is_current_page(self, page_key: str) -> bool:
        """Check if the given page key is the current page"""
        return self.get_current_page() == page_key