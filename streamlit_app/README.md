# Synapse-Lite Fraud Detection System

A modular Streamlit application for real-time Bitcoin transaction monitoring and AI-powered fraud detection.

## Project Structure

The application has been refactored from a single large file into a modular structure for better maintainability:

```
streamlit_app/
├── streamlit_app.py          # Main application entry point
├── config.py                 # Configuration constants and settings
├── styling.py               # CSS styling definitions
├── utils.py                 # Helper functions and utilities
├── data_generator.py        # Dummy data generation functions
├── charts.py                # Chart creation functions (Plotly)
├── sidebar.py               # Sidebar component
├── pages/                   # Individual page modules
│   ├── __init__.py
│   ├── dashboard.py         # Main dashboard page
│   ├── transactions.py      # Transaction monitoring page
│   ├── alerts.py           # Security alerts page
│   ├── analytics.py        # Analytics and reporting page
│   └── settings.py         # System settings page
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
└── README.md               # This file
```

## Modules Overview

### Core Application Files

- **`streamlit_app.py`**: Main entry point that orchestrates the entire application
- **`config.py`**: Contains all configuration constants (BTC rate, page settings, navigation)
- **`styling.py`**: Centralized CSS styling with Coinbase-inspired design
- **`utils.py`**: Utility functions for UI components and risk calculations
- **`sidebar.py`**: Reusable sidebar component with navigation and system status

### Data and Visualization

- **`data_generator.py`**: Functions for generating dummy transaction and alert data
- **`charts.py`**: Plotly chart creation functions for analytics dashboards

### Page Modules

Each page is a separate module with its own `render_*()` function:

- **`dashboard.py`**: Main overview with metrics, charts, and recent activity
- **`transactions.py`**: Real-time transaction monitoring and filtering
- **`alerts.py`**: Security alerts management and investigation
- **`analytics.py`**: Advanced analytics with trends and pattern analysis
- **`settings.py`**: System configuration and preferences

## Benefits of Modular Structure

1. **Maintainability**: Each component has a single responsibility
2. **Scalability**: Easy to add new pages or modify existing ones
3. **Reusability**: Components can be reused across different parts of the app
4. **Team Development**: Multiple developers can work on different modules
5. **Testing**: Individual modules can be tested in isolation
6. **Performance**: Lazy loading of page-specific functionality

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

## Docker Support

```bash
# Build the image
docker build -t synapse-lite .

# Run the container
docker run -p 8501:8501 synapse-lite
```

## Adding New Pages

To add a new page:

1. Create a new file in `pages/` directory (e.g., `pages/reports.py`)
2. Implement a `render_reports()` function
3. Add the page to `PAGES` dict in `config.py`
4. Import and route the page in `streamlit_app.py`

## Code Organization Principles

- **Separation of Concerns**: Each file has a specific purpose
- **Import Management**: Relative imports prevent circular dependencies
- **Configuration Centralization**: All constants in `config.py`
- **UI Consistency**: Shared styling and utility functions
- **Data Abstraction**: Data generation separated from presentation

This modular structure makes the codebase much more manageable and sets up a strong foundation for future development.