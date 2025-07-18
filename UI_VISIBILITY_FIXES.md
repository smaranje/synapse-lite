# UI Visibility Fixes Summary

## Changes Made

### 1. Removed "Using Dummy Data" Indicator
- Removed the data source indicator section from the sidebar
- Cleaned up extra divider lines
- Service status indicators now appear directly after the quick stats

### 2. Fixed Pie Chart Overlapping Labels
- Changed text position from 'inside' to 'auto' for better label placement
- Added text font size specification (12px)
- Added border lines to pie slices for better separation
- Added proper margins to prevent cutoff

### 3. Fixed Theme Dropdown Visibility
- Added comprehensive CSS for dropdown popover styling
- Fixed background colors for dropdown menu
- Added hover states for options
- Ensured selected option is highlighted properly
- Added proper borders and shadows for visibility

### 4. Fixed Chart Backgrounds in Dark Mode
- Made plotly chart backgrounds transparent
- Fixed SVG container backgrounds
- Ensured charts blend with the dark theme
- Added specific fixes for pie chart text visibility with stroke

### 5. Improved Chart Theme Selection
- Added automatic theme detection based on dark/light mode
- Expanded theme options to include "simple_white" and "none"
- Default theme now matches the current mode (plotly_dark for dark mode)

## CSS Additions

```css
/* Fix selectbox dropdown menu visibility */
[data-baseweb="popover"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    box-shadow: var(--shadow-md) !important;
}

[data-baseweb="popover"] [role="listbox"] {
    background: var(--bg-card) !important;
    max-height: 300px !important;
    overflow-y: auto !important;
}

[data-baseweb="popover"] [role="option"] {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    padding: 8px 12px !important;
}

[data-baseweb="popover"] [role="option"]:hover {
    background: var(--bg-secondary) !important;
}

[data-baseweb="popover"] [role="option"][aria-selected="true"] {
    background: var(--primary-color) !important;
    color: white !important;
}

/* Fix plotly chart backgrounds in dark mode */
.js-plotly-plot .plotly .main-svg {
    background: transparent !important;
}

.js-plotly-plot .plotly .svg-container {
    background: transparent !important;
}

.plotly-graph-div {
    background: transparent !important;
}

/* Ensure pie chart text is visible */
.js-plotly-plot .plotly .pie text {
    fill: white !important;
    stroke: rgba(0,0,0,0.5) !important;
    stroke-width: 0.5px !important;
}
```

## Result

The application now has:
- Cleaner sidebar without unnecessary indicators
- Properly visible dropdown menus with correct styling
- Charts that blend seamlessly with dark/light themes
- No overlapping text in pie charts
- Better overall visual consistency across all components