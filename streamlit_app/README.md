# Simple Streamlit Application

A feature-rich Streamlit application demonstrating various interactive components and data visualization capabilities.

## Features

- 📊 **Interactive Data Visualization**: Line charts, bar charts, and scatter plots using Plotly
- 📈 **Real-time Statistics**: Dynamic metrics and data tables
- 📁 **File Upload**: CSV file upload and analysis functionality
- 🎮 **Interactive Widgets**: Sliders, buttons, text inputs, color pickers, and more
- 🎨 **Customizable UI**: Sidebar configuration and responsive layout

## Prerequisites

- Python 3.11 or higher
- Docker (optional, for containerized deployment)

## Installation & Running

### Option 1: Run locally with Python

1. Navigate to the streamlit_app directory:
   ```bash
   cd streamlit_app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run streamlit_app.py
   ```

4. Open your browser and navigate to `http://localhost:8501`

### Option 2: Run with Docker

1. Navigate to the streamlit_app directory:
   ```bash
   cd streamlit_app
   ```

2. Build the Docker image:
   ```bash
   docker build -t streamlit-app .
   ```

3. Run the container:
   ```bash
   docker run -p 8501:8501 streamlit-app
   ```

4. Open your browser and navigate to `http://localhost:8501`

## Usage

### Sidebar Configuration
- Enter your name for personalized charts
- Adjust the number of data points using the slider
- Select different chart types
- Choose custom colors for visualizations

### Main Features
- **Data Visualization**: View dynamically generated charts based on your configuration
- **Statistics**: Monitor real-time metrics and recent data
- **File Upload**: Upload CSV files for analysis and visualization
- **Interactive Elements**: Experiment with various Streamlit widgets

## Project Structure

```
streamlit_app/
├── streamlit_app.py    # Main application file
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
└── README.md         # This file
```

## Dependencies

- **streamlit**: Core framework for the web application
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **plotly**: Interactive data visualization
- **altair**: Declarative visualization library

## Customization

You can easily extend this application by:
- Adding new chart types in the visualization section
- Implementing additional file formats for upload
- Creating new interactive widgets
- Adding database connectivity for persistent data
- Implementing user authentication

## Troubleshooting

If you encounter any issues:

1. **Port already in use**: Change the port by running:
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```

2. **Module not found**: Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Docker build fails**: Make sure Docker is running and you have sufficient permissions

## License

This is a sample application for demonstration purposes.