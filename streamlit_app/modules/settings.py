"""
Settings page for the Synapse-Lite Fraud Detection System
Configuration options for data sources, services, and display preferences
"""

import streamlit as st
import os
from utils import service_integration

def show():
    """Display the settings page"""
    st.title("Settings")
    
    # Create tabs for different settings categories
    tab1, tab2, tab3, tab4 = st.tabs(["Data Source", "Service Configuration", "Display Settings", "System Info"])
    
    with tab1:
        st.markdown("### Data Source Configuration")
        
        # Data source toggle
        use_dummy = st.checkbox(
            "Use Dummy Data",
            value=st.session_state.USE_DUMMY_DATA,
            help="Toggle between dummy data and real service connections"
        )
        
        if use_dummy != st.session_state.USE_DUMMY_DATA:
            st.session_state.USE_DUMMY_DATA = use_dummy
            st.success("Data source updated. Click 'Apply Changes' to reload data.")
        
        if not use_dummy:
            st.markdown("#### Neo4j Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                neo4j_uri = st.text_input(
                    "Neo4j URI",
                    value=os.getenv("NEO4J_URI", "bolt://neo4j:7687"),
                    help="Neo4j database connection URI"
                )
                
                neo4j_username = st.text_input(
                    "Neo4j Username",
                    value=os.getenv("NEO4J_USERNAME", "neo4j"),
                    help="Neo4j authentication username"
                )
            
            with col2:
                neo4j_password = st.text_input(
                    "Neo4j Password",
                    value="*" * len(os.getenv("NEO4J_PASSWORD", "password")),
                    type="password",
                    help="Neo4j authentication password"
                )
                
                if st.button("Test Neo4j Connection"):
                    with st.spinner("Testing connection..."):
                        neo4j_conn = service_integration.Neo4jConnection()
                        neo4j_conn.uri = neo4j_uri
                        neo4j_conn.username = neo4j_username
                        if neo4j_password != "*" * len(os.getenv("NEO4J_PASSWORD", "password")):
                            neo4j_conn.password = neo4j_password
                        
                        if neo4j_conn.connect():
                            st.success("✅ Successfully connected to Neo4j!")
                            neo4j_conn.close()
                        else:
                            st.error("❌ Failed to connect to Neo4j. Please check your credentials.")
            
            st.markdown("#### Kafka Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                kafka_broker = st.text_input(
                    "Kafka Broker",
                    value=os.getenv("KAFKA_BROKER", "kafka:9092"),
                    help="Kafka broker address"
                )
                
                kafka_topic = st.text_input(
                    "Kafka Topic",
                    value=os.getenv("KAFKA_TOPIC", "transactions"),
                    help="Kafka topic for transaction stream"
                )
            
            with col2:
                kafka_group_id = st.text_input(
                    "Consumer Group ID",
                    value="streamlit-dashboard",
                    help="Kafka consumer group identifier"
                )
                
                if st.button("Test Kafka Connection"):
                    with st.spinner("Testing connection..."):
                        kafka_conn = service_integration.KafkaConnection()
                        kafka_conn.bootstrap_servers = kafka_broker
                        kafka_conn.topic = kafka_topic
                        
                        if kafka_conn.create_consumer(kafka_group_id):
                            st.success("✅ Successfully connected to Kafka!")
                            kafka_conn.close()
                        else:
                            st.error("❌ Failed to connect to Kafka. Please check your configuration.")
    
    with tab2:
        st.markdown("### 🤖 Service Configuration")
        
        st.markdown("#### LLM Service (Gemini API)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            llm_service_url = st.text_input(
                "LLM Service URL",
                value=os.getenv("LLM_SERVICE_URL", "http://flask-llm-service:5000"),
                help="Flask LLM service endpoint"
            )
            
            gemini_api_key = st.text_input(
                "Gemini API Key",
                value="*" * 20 if os.getenv("GEMINI_API_KEY") else "",
                type="password",
                help="Google Gemini API key for SAR generation"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Test LLM Service"):
                with st.spinner("Testing connection..."):
                    llm_conn = service_integration.LLMServiceConnection()
                    llm_conn.base_url = llm_service_url
                    
                    if llm_conn.check_health():
                        st.success("✅ LLM Service is healthy!")
                    else:
                        st.error("❌ LLM Service is not responding. Please check if it's running.")
            
            if st.button("Test SAR Generation"):
                with st.spinner("Generating test SAR..."):
                    test_alert = {
                        'alert_id': 'TEST-001',
                        'transaction_hash': 'test_hash_123',
                        'risk_level': 'High',
                        'ml_score': 0.85,
                        'total_value_btc': 1.5,
                        'total_value_usd': 67500,
                        'description': 'Test transaction for SAR generation'
                    }
                    
                    llm_conn = service_integration.LLMServiceConnection()
                    llm_conn.base_url = llm_service_url
                    sar_text = llm_conn.generate_sar(test_alert)
                    
                    if "Error" not in sar_text:
                        st.success("✅ SAR generated successfully!")
                        with st.expander("View Test SAR"):
                            st.text(sar_text)
                    else:
                        st.error(f"❌ {sar_text}")
        
        st.markdown("#### Alert Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            risk_thresholds = st.slider(
                "Critical Risk Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.8,
                step=0.05,
                help="ML score threshold for critical risk classification"
            )
            
            high_risk_threshold = st.slider(
                "High Risk Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.6,
                step=0.05,
                help="ML score threshold for high risk classification"
            )
        
        with col2:
            medium_risk_threshold = st.slider(
                "Medium Risk Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.4,
                step=0.05,
                help="ML score threshold for medium risk classification"
            )
            
            smurfing_output_threshold = st.number_input(
                "Smurfing Output Threshold",
                min_value=5,
                max_value=100,
                value=10,
                help="Minimum number of outputs to trigger smurfing detection"
            )
    
    with tab3:
        st.markdown("### Display Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Refresh Settings")
            
            refresh_interval = st.slider(
                "Auto-refresh interval (seconds)",
                min_value=1,
                max_value=60,
                value=int(os.getenv("REFRESH_INTERVAL", "5")),
                help="How often to refresh data automatically"
            )
            
            max_display_transactions = st.number_input(
                "Max Transactions to Display",
                min_value=10,
                max_value=500,
                value=100,
                help="Maximum number of transactions to show at once"
            )
            
            max_display_alerts = st.number_input(
                "Max Alerts to Display",
                min_value=10,
                max_value=100,
                value=50,
                help="Maximum number of alerts to show at once"
            )
        
        with col2:
            st.markdown("#### Chart Settings")
            
            default_chart_theme = st.selectbox(
                "Default Chart Theme",
                ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"],
                index=1,
                help="Default theme for all charts"
            )
            
            enable_animations = st.checkbox(
                "Enable Chart Animations",
                value=True,
                help="Toggle animations in charts"
            )
            
            show_confidence_bands = st.checkbox(
                "Show Confidence Bands",
                value=True,
                help="Display confidence bands in time series charts"
            )
        
        st.markdown("#### Notification Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_sound_alerts = st.checkbox(
                "Enable Sound Alerts",
                value=False,
                help="Play sound for critical alerts"
            )
            
            enable_desktop_notifications = st.checkbox(
                "Enable Desktop Notifications",
                value=False,
                help="Show desktop notifications for new alerts"
            )
        
        with col2:
            critical_alert_email = st.text_input(
                "Critical Alert Email",
                placeholder="alerts@company.com",
                help="Email address for critical alert notifications"
            )
            
            alert_digest_frequency = st.selectbox(
                "Alert Digest Frequency",
                ["Never", "Hourly", "Daily", "Weekly"],
                help="How often to send alert summary emails"
            )
    
    with tab4:
        st.markdown("### System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Service Status")
            
            for service, status in st.session_state.service_status.items():
                if status:
                    st.success(f"{service}: Connected")
                else:
                    st.info(f"{service}: Disconnected")
        
        with col2:
            st.markdown("#### System Metrics")
            
            st.metric("Total Transactions", len(st.session_state.transactions))
            st.metric("Active Alerts", len([a for a in st.session_state.alerts if a['status'] == 'Open']))
            st.metric("Last Refresh", st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S'))
            
            if st.button("Clear Cache"):
                st.cache_data.clear()
                st.cache_resource.clear()
                st.success("Cache cleared successfully!")
        
        st.markdown("#### Environment Variables")
        
        with st.expander("View Environment Configuration"):
            env_vars = {
                "NEO4J_URI": os.getenv("NEO4J_URI", "Not set"),
                "NEO4J_USERNAME": os.getenv("NEO4J_USERNAME", "Not set"),
                "KAFKA_BROKER": os.getenv("KAFKA_BROKER", "Not set"),
                "KAFKA_TOPIC": os.getenv("KAFKA_TOPIC", "Not set"),
                "LLM_SERVICE_URL": os.getenv("LLM_SERVICE_URL", "Not set"),
                "USE_DUMMY_DATA": os.getenv("USE_DUMMY_DATA", "Not set"),
                "GEMINI_API_KEY": "***SET***" if os.getenv("GEMINI_API_KEY") else "Not set"
            }
            
            for var, value in env_vars.items():
                st.text(f"{var}: {value}")
        
        st.markdown("#### Export/Import Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export Configuration"):
                config = {
                    "data_source": {
                        "use_dummy_data": st.session_state.USE_DUMMY_DATA,
                        "neo4j_uri": os.getenv("NEO4J_URI", ""),
                        "kafka_broker": os.getenv("KAFKA_BROKER", ""),
                        "kafka_topic": os.getenv("KAFKA_TOPIC", "")
                    },
                    "services": {
                        "llm_service_url": os.getenv("LLM_SERVICE_URL", "")
                    },
                    "display": {
                        "refresh_interval": refresh_interval,
                        "max_transactions": max_display_transactions,
                        "max_alerts": max_display_alerts
                    }
                }
                
                import json
                config_json = json.dumps(config, indent=2)
                
                st.download_button(
                    label="Download Configuration",
                    data=config_json,
                    file_name="synapse_config.json",
                    mime="application/json"
                )
        
        with col2:
            uploaded_config = st.file_uploader(
                "Import Configuration",
                type="json",
                help="Upload a configuration file to restore settings"
            )
            
            if uploaded_config is not None:
                import json
                config = json.load(uploaded_config)
                st.success("Configuration loaded! Apply changes to update settings.")
                st.json(config)
    
    # Apply changes button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("Apply Changes", type="primary"):
            st.success("Settings applied successfully!")
            st.rerun()
    
    with col2:
        if st.button("Reset to Defaults"):
            st.session_state.USE_DUMMY_DATA = True
            st.success("Settings reset to defaults!")
            st.rerun()