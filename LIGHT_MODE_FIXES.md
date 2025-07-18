# Light Mode Visibility Fixes

## Issues Addressed

1. **KPI Cards Contrast** - White text on blue background had poor readability
2. **Chart Text Visibility** - Chart labels and axis text were not visible
3. **Sidebar Text** - Some sidebar elements had poor contrast
4. **Pie Chart Labels** - Text on pie charts was hard to read

## Solutions Implemented

### 1. Enhanced KPI Cards
- Added gradient background for better visual depth
- Added text shadows to improve readability
- Increased opacity of text elements
- Used darker blue gradient (primary to primary-hover)

### 2. Chart Visibility Improvements
- Added proper font colors for all chart text
- Set axis line colors for better visibility
- Configured tick font colors
- Added stroke to pie chart text for better contrast

### 3. Light Mode Specific CSS
```css
/* Fix chart text visibility in light mode */
.js-plotly-plot .plotly text {
    fill: #050f19 !important;
}

/* Fix pie chart text in light mode */
.js-plotly-plot .plotly .pie text {
    fill: #050f19 !important;
    stroke: rgba(255,255,255,0.8) !important;
    stroke-width: 2px !important;
    font-weight: 600 !important;
}

/* Ensure axis lines are visible */
.js-plotly-plot .plotly .crisp {
    stroke: #e5e7eb !important;
}

/* Fix grid lines */
.js-plotly-plot .plotly .gridlayer line {
    stroke: #f0f2f5 !important;
}

/* Fix sidebar text visibility in light mode */
[data-testid="stSidebar"] {
    background: #fafbfc !important;
}

[data-testid="stSidebar"] .stRadio > div > label {
    color: #050f19 !important;
}

[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] h4 {
    color: #050f19 !important;
}
```

### 4. Text Enhancement
- Added text shadows to KPI card elements:
  - Labels: `text-shadow: 0 1px 2px rgba(0,0,0,0.1)`
  - Values: `text-shadow: 0 1px 3px rgba(0,0,0,0.15)`
  - Deltas: `text-shadow: 0 1px 2px rgba(0,0,0,0.1)`

### 5. Chart Configuration Updates
- Set proper font colors in chart layouts
- Added axis line colors
- Configured tick fonts with appropriate colors
- Set global font color for charts

## Result

The application now has:
- Excellent readability in light mode
- Proper contrast for all text elements
- Visible chart elements with appropriate colors
- Consistent styling across all components
- Better visual hierarchy with subtle shadows and gradients