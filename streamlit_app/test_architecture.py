#!/usr/bin/env python3
"""
Test script to verify the re-engineered Streamlit application architecture.
This tests the core modules without requiring external dependencies.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test that all core modules can be imported"""
    print("Testing core module imports...")
    
    try:
        from core.app_state import AppState
        print("✅ AppState imported successfully")
    except Exception as e:
        print(f"❌ AppState import failed: {e}")
        return False
    
    try:
        from core.theme_manager import ThemeManager
        print("✅ ThemeManager imported successfully")
    except Exception as e:
        print(f"❌ ThemeManager import failed: {e}")
        return False
    
    try:
        from core.navigation import NavigationManager
        print("✅ NavigationManager imported successfully")
    except Exception as e:
        print(f"❌ NavigationManager import failed: {e}")
        return False
    
    try:
        from data.mock_data_generator import MockDataGenerator
        print("✅ MockDataGenerator imported successfully")
    except Exception as e:
        print(f"❌ MockDataGenerator import failed: {e}")
        return False
    
    try:
        from data.data_service import DataService
        print("✅ DataService imported successfully")
    except Exception as e:
        print(f"❌ DataService import failed: {e}")
        return False
    
    return True

def test_app_state():
    """Test AppState functionality"""
    print("\nTesting AppState functionality...")
    
    try:
        # Test without Streamlit session state
        app_state = AppState()
        
        # Test settings
        default_settings = app_state._load_default_settings()
        assert isinstance(default_settings, dict)
        assert 'theme' in default_settings
        print("✅ AppState settings loaded correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ AppState test failed: {e}")
        return False

def test_navigation():
    """Test NavigationManager functionality"""
    print("\nTesting NavigationManager functionality...")
    
    try:
        nav = NavigationManager()
        
        # Test page configuration
        pages = nav.get_all_pages()
        assert isinstance(pages, dict)
        assert 'overview' in pages
        assert 'transactions' in pages
        print("✅ NavigationManager pages configured correctly")
        
        # Test categories
        categories = nav.get_page_categories()
        assert isinstance(categories, list)
        assert 'main' in categories
        print("✅ NavigationManager categories working")
        
        return True
        
    except Exception as e:
        print(f"❌ NavigationManager test failed: {e}")
        return False

def test_theme_manager():
    """Test ThemeManager functionality"""
    print("\nTesting ThemeManager functionality...")
    
    try:
        theme_mgr = ThemeManager()
        
        # Test theme configurations
        dark_theme = theme_mgr._get_dark_theme()
        light_theme = theme_mgr._get_light_theme()
        
        assert isinstance(dark_theme, dict)
        assert isinstance(light_theme, dict)
        assert 'primary_bg' in dark_theme
        assert 'primary_bg' in light_theme
        print("✅ ThemeManager themes configured correctly")
        
        # Test CSS generation
        css = theme_mgr._generate_css(dark_theme)
        assert isinstance(css, str)
        assert 'var(--primary-bg)' in css
        print("✅ ThemeManager CSS generation working")
        
        return True
        
    except Exception as e:
        print(f"❌ ThemeManager test failed: {e}")
        return False

def test_data_layer():
    """Test data layer functionality"""
    print("\nTesting data layer functionality...")
    
    try:
        # Test MockDataGenerator
        generator = MockDataGenerator()
        
        transactions = generator.generate_transactions(10)
        assert isinstance(transactions, list)
        assert len(transactions) == 10
        assert all('hash' in t for t in transactions)
        print("✅ MockDataGenerator working correctly")
        
        alerts = generator.generate_alerts(5)
        assert isinstance(alerts, list)
        assert len(alerts) == 5
        print("✅ MockDataGenerator alerts working correctly")
        
        # Test DataService  
        data_service = DataService()
        
        # Test data generation
        transactions = data_service.get_recent_transactions(5)
        assert isinstance(transactions, list)
        print("✅ DataService working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Data layer test failed: {e}")
        return False

def test_architecture():
    """Test the overall architecture"""
    print("🚀 Testing Synapse-Lite Re-engineered Architecture")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_app_state,
        test_navigation,
        test_theme_manager,
        test_data_layer
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Architecture is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = test_architecture()
    sys.exit(0 if success else 1)