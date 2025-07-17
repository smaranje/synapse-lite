# Analytics page module

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from charts import (
    create_weekly_trends_chart,
    create_detection_accuracy_chart,
    create_volume_vs_risk_scatter,
    create_geographic_distribution_chart,
    create_time_series_chart,
    create_heatmap_chart
)
from data_generator import generate_monthly_data, generate_system_metrics

def render_analytics():
    """Render the advanced analytics and trends page"""
    st.title("📊 Analytics")
    st.markdown("### Advanced Fraud Detection Analytics & Insights")
    
    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🎯 Performance", "🗺️ Geographic", "🔥 Patterns"])
    
    with tab1:
        st.markdown("## Trend Analysis")
        
        # Time period selector
        col1, col2 = st.columns([3, 1])
        with col2:
            time_period = st.selectbox("Time Period", ["7 days", "30 days", "90 days"], index=1)
        
        # Extract number of days
        days = int(time_period.split()[0])
        
        # Time series chart
        st.markdown("### Historical Trends")
        fig_timeseries = create_time_series_chart(days)
        st.plotly_chart(fig_timeseries, use_container_width=True)
        
        # Weekly trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Weekly Risk Trends")
            fig_weekly = create_weekly_trends_chart()
            st.plotly_chart(fig_weekly, use_container_width=True)
        
        with col2:
            st.markdown("### Monthly Detection Accuracy")
            fig_accuracy = create_detection_accuracy_chart()
            st.plotly_chart(fig_accuracy, use_container_width=True)
        
        # Trend insights
        st.markdown("---")
        st.markdown("### Key Insights")
        
        insight_col1, insight_col2, insight_col3 = st.columns(3)
        
        with insight_col1:
            st.markdown("""
            <div style="padding: 1rem; background: linear-gradient(135deg, #0052ff 0%, #0046cc 100%); border-radius: 12px; color: white;">
                <h4 style="margin: 0 0 0.5rem 0; color: white;">📈 Trend Direction</h4>
                <p style="margin: 0; font-size: 0.875rem;">Risk scores have decreased by 12% over the past month, indicating improved system performance.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with insight_col2:
            st.markdown("""
            <div style="padding: 1rem; background: linear-gradient(135deg, #059669 0%, #047857 100%); border-radius: 12px; color: white;">
                <h4 style="margin: 0 0 0.5rem 0; color: white;">🎯 Detection Rate</h4>
                <p style="margin: 0; font-size: 0.875rem;">False positive rate reduced to 3.2%, the lowest in 6 months.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with insight_col3:
            st.markdown("""
            <div style="padding: 1rem; background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%); border-radius: 12px; color: white;">
                <h4 style="margin: 0 0 0.5rem 0; color: white;">⚠️ Peak Hours</h4>
                <p style="margin: 0; font-size: 0.875rem;">Highest risk activity occurs between 2-4 AM UTC daily.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("## Performance Metrics")
        
        # Performance indicators
        metrics = generate_system_metrics()
        monthly_data = generate_monthly_data()
        
        # KPI cards
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        
        with kpi_col1:
            st.metric(
                "Detection Accuracy",
                f"{metrics['detection_accuracy']:.1f}%",
                "+2.3%"
            )
        
        with kpi_col2:
            st.metric(
                "False Positive Rate",
                f"{metrics['false_positive_rate']:.1f}%",
                "-0.8%"
            )
        
        with kpi_col3:
            st.metric(
                "Processing Speed",
                f"{metrics['processing_speed']} tx/min",
                "+15%"
            )
        
        with kpi_col4:
            st.metric(
                "System Uptime",
                f"{metrics['system_uptime']:.2f}%",
                "0.01%"
            )
        
        # Performance charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Volume vs Risk Analysis")
            fig_scatter = create_volume_vs_risk_scatter()
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            st.markdown("### Risk Pattern Heatmap")
            fig_heatmap = create_heatmap_chart()
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Performance breakdown
        st.markdown("---")
        st.markdown("### Model Performance Breakdown")
        
        perf_col1, perf_col2 = st.columns(2)
        
        with perf_col1:
            st.markdown("#### ML Model Metrics")
            st.markdown("""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #f0f3f7;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <div style="color: #6b7280; font-size: 0.875rem;">Precision</div>
                        <div style="font-weight: 600; font-size: 1.25rem; color: #059669;">94.2%</div>
                    </div>
                    <div>
                        <div style="color: #6b7280; font-size: 0.875rem;">Recall</div>
                        <div style="font-weight: 600; font-size: 1.25rem; color: #0052ff;">91.8%</div>
                    </div>
                    <div>
                        <div style="color: #6b7280; font-size: 0.875rem;">F1-Score</div>
                        <div style="font-weight: 600; font-size: 1.25rem; color: #ea580c;">93.0%</div>
                    </div>
                    <div>
                        <div style="color: #6b7280; font-size: 0.875rem;">AUC-ROC</div>
                        <div style="font-weight: 600; font-size: 1.25rem; color: #dc2626;">0.956</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with perf_col2:
            st.markdown("#### Rule Engine Metrics")
            st.markdown("""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #f0f3f7;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <div style="color: #6b7280; font-size: 0.875rem;">Rules Active</div>
                        <div style="font-weight: 600; font-size: 1.25rem; color: #059669;">47</div>
                    </div>
                    <div>
                        <div style="color: #6b7280; font-size: 0.875rem;">Hit Rate</div>
                        <div style="font-weight: 600; font-size: 1.25rem; color: #0052ff;">23.4%</div>
                    </div>
                    <div>
                        <div style="color: #6b7280; font-size: 0.875rem;">Avg Response</div>
                        <div style="font-weight: 600; font-size: 1.25rem; color: #ea580c;">45ms</div>
                    </div>
                    <div>
                        <div style="color: #6b7280; font-size: 0.875rem;">Coverage</div>
                        <div style="font-weight: 600; font-size: 1.25rem; color: #dc2626;">87.3%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("## Geographic Analysis")
        
        # Geographic distribution
        st.markdown("### Transaction Distribution by Country")
        fig_geo = create_geographic_distribution_chart()
        st.plotly_chart(fig_geo, use_container_width=True)
        
        # Risk analysis by region
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### High-Risk Regions")
            st.markdown("""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #f0f3f7;">
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f0f3f7;">
                        <span>🔴 Eastern Europe</span>
                        <span style="font-weight: 600; color: #dc2626;">High Risk</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f0f3f7;">
                        <span>🟠 Southeast Asia</span>
                        <span style="font-weight: 600; color: #ea580c;">Medium Risk</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f0f3f7;">
                        <span>🟡 Latin America</span>
                        <span style="font-weight: 600; color: #0052ff;">Medium Risk</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0;">
                        <span>🟢 North America</span>
                        <span style="font-weight: 600; color: #059669;">Low Risk</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Volume by Region")
            st.markdown("""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #f0f3f7;">
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f0f3f7;">
                        <span>🇺🇸 United States</span>
                        <span style="font-weight: 600;">₿2,847.32</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f0f3f7;">
                        <span>🇬🇧 United Kingdom</span>
                        <span style="font-weight: 600;">₿1,923.14</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f0f3f7;">
                        <span>🇩🇪 Germany</span>
                        <span style="font-weight: 600;">₿1,456.78</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0;">
                        <span>🇯🇵 Japan</span>
                        <span style="font-weight: 600;">₿987.45</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("## Pattern Analysis")
        
        # Pattern detection insights
        st.markdown("### Fraud Pattern Detection")
        
        pattern_col1, pattern_col2 = st.columns(2)
        
        with pattern_col1:
            st.markdown("#### Common Fraud Patterns")
            st.markdown("""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #f0f3f7;">
                <div style="margin-bottom: 0.5rem; padding: 0.75rem; background: #fef2f2; border-radius: 6px; border-left: 4px solid #dc2626;">
                    <div style="font-weight: 600; color: #dc2626;">Smurfing Pattern</div>
                    <div style="font-size: 0.875rem; color: #6b7280;">Multiple small transactions to avoid detection limits</div>
                    <div style="font-size: 0.75rem; color: #dc2626; margin-top: 0.25rem;">Detected: 23 instances this week</div>
                </div>
                
                <div style="margin-bottom: 0.5rem; padding: 0.75rem; background: #fef3c7; border-radius: 6px; border-left: 4px solid #ea580c;">
                    <div style="font-weight: 600; color: #ea580c;">Round Amount Pattern</div>
                    <div style="font-size: 0.875rem; color: #6b7280;">Transactions in exact round numbers</div>
                    <div style="font-size: 0.75rem; color: #ea580c; margin-top: 0.25rem;">Detected: 45 instances this week</div>
                </div>
                
                <div style="margin-bottom: 0.5rem; padding: 0.75rem; background: #eff6ff; border-radius: 6px; border-left: 4px solid #0052ff;">
                    <div style="font-weight: 600; color: #0052ff;">Velocity Anomaly</div>
                    <div style="font-size: 0.875rem; color: #6b7280;">Unusual transaction frequency patterns</div>
                    <div style="font-size: 0.75rem; color: #0052ff; margin-top: 0.25rem;">Detected: 12 instances this week</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with pattern_col2:
            st.markdown("#### Risk Score Distribution")
            st.markdown("""
            <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #f0f3f7;">
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span>Critical (80-100%)</span>
                        <span style="font-weight: 600; color: #dc2626;">127 tx</span>
                    </div>
                    <div style="background: #f3f4f6; border-radius: 4px; height: 8px;">
                        <div style="background: #dc2626; width: 12%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span>High (60-79%)</span>
                        <span style="font-weight: 600; color: #ea580c;">234 tx</span>
                    </div>
                    <div style="background: #f3f4f6; border-radius: 4px; height: 8px;">
                        <div style="background: #ea580c; width: 23%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span>Medium (40-59%)</span>
                        <span style="font-weight: 600; color: #0052ff;">456 tx</span>
                    </div>
                    <div style="background: #f3f4f6; border-radius: 4px; height: 8px;">
                        <div style="background: #0052ff; width: 45%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
                
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span>Low (0-39%)</span>
                        <span style="font-weight: 600; color: #059669;">789 tx</span>
                    </div>
                    <div style="background: #f3f4f6; border-radius: 4px; height: 8px;">
                        <div style="background: #059669; width: 78%; height: 100%; border-radius: 4px;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Advanced pattern analysis
        st.markdown("---")
        st.markdown("### Advanced Pattern Insights")
        
        insight_col1, insight_col2, insight_col3 = st.columns(3)
        
        with insight_col1:
            st.markdown("#### Temporal Patterns")
            st.markdown("""
            - Peak fraud activity: **2-4 AM UTC**
            - Lowest activity: **10-12 PM UTC**  
            - Weekend increase: **+15%**
            - Holiday spikes: **+45%**
            """)
        
        with insight_col2:
            st.markdown("#### Behavioral Patterns")
            st.markdown("""
            - Round amount preference: **67%**
            - Multiple small tx: **34%**
            - Cross-border patterns: **23%**
            - VPN usage correlation: **78%**
            """)
        
        with insight_col3:
            st.markdown("#### Network Analysis")
            st.markdown("""
            - Connected addresses: **156**
            - Cluster analysis: **12 groups**
            - Hub detection: **3 major hubs**
            - Suspicious networks: **7 active**
            """)