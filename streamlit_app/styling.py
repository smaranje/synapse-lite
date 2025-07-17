import streamlit as st

def apply_styling():
    """Apply essential CSS styling to the Streamlit app."""
    st.markdown("""
        <style>
        .metric-card {
            background: #ffffff;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #f0f3f7;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
            margin-bottom: 1rem;
            transition: all 0.2s ease;
        }
        
        .metric-value {
            font-size: 2.25rem;
            font-weight: 600;
            color: #0052ff;
            margin: 0.5rem 0;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: #5b616e;
            font-weight: 500;
        }
        
        .metric-delta {
            font-size: 0.75rem;
            font-weight: 500;
            margin-top: 0.5rem;
        }
        
        .metric-delta.positive { color: #05d168; }
        .metric-delta.negative { color: #ff4747; }
        .metric-delta.neutral { color: #f4c430; }
        
        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.375rem 0.875rem;
            border-radius: 24px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .status-live { background: #05d168; color: white; }
        .status-warning { background: #f4c430; color: #0a0b0d; }
        .status-critical { background: #ff4747; color: white; }
        
        .alert-card {
            background: #ffffff;
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 3px solid #0052ff;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }
        
        .alert-card.critical { border-left-color: #ff4747; }
        .alert-card.high { border-left-color: #f4c430; }
        .alert-card.medium { border-left-color: #0052ff; }
        .alert-card.low { border-left-color: #05d168; }
        
        .transaction-card {
            background: #ffffff;
            padding: 1.25rem;
            border-radius: 12px;
            border: 1px solid #f0f3f7;
            margin-bottom: 0.75rem;
        }
        
        .risk-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .risk-badge.critical { background: #f56565; color: white; }
        .risk-badge.high { background: #ed8936; color: white; }
        .risk-badge.medium { background: #4299e1; color: white; }
        .risk-badge.low { background: #48bb78; color: white; }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #718096;
            font-size: 0.9rem;
            border-top: 1px solid #2d3748;
            margin-top: 3rem;
        }
        </style>
    """, unsafe_allow_html=True)