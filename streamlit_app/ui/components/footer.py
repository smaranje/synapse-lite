"""
Footer Manager for Synapse-Lite
Application footer with system information and links
"""

import streamlit as st
from datetime import datetime

class FooterManager:
    """Manages the application footer"""
    
    def render(self):
        """Render the application footer"""
        st.markdown("---")
        
        # Create footer layout
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            self._render_system_info()
        
        with col2:
            self._render_links()
        
        with col3:
            self._render_version_info()
        
        # Copyright and attribution
        self._render_copyright()
    
    def _render_system_info(self):
        """Render system information"""
        st.markdown("""
            **Synapse-Lite Fraud Detection System**
            
            Real-time Bitcoin transaction monitoring and AI-powered threat detection for enterprise security.
            
            🔷 **Features:**
            - Real-time transaction analysis
            - AI-powered fraud detection  
            - Advanced analytics dashboard
            - Investigation case management
        """)
    
    def _render_links(self):
        """Render useful links"""
        st.markdown("""
            **Resources**
            
            📖 [Documentation](#) | 🐛 [Report Issues](#) | 💬 [Support](#)
            
            🔗 **Quick Links:**
            - [System Health](#)
            - [API Documentation](#)
            - [User Guide](#)
            - [Security Policy](#)
        """)
    
    def _render_version_info(self):
        """Render version and build information"""
        build_date = datetime.now().strftime("%Y-%m-%d")
        
        st.markdown(f"""
            **System Info**
            
            Version: 2.0.0  
            Build: {build_date}  
            Status: 🟢 Online  
            Uptime: 99.9%
            
            Environment: Production  
            Region: US-East-1
        """)
    
    def _render_copyright(self):
        """Render copyright and attribution"""
        current_year = datetime.now().year
        
        st.markdown(f"""
            <div class="app-footer">
                <div style="text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                    <p style="margin: 0.5rem 0; color: var(--secondary-text);">
                        © {current_year} Synapse-Lite Fraud Detection System
                    </p>
                    <p style="margin: 0.5rem 0; font-size: 0.8rem; color: var(--secondary-text);">
                        Built with ❤️ using Streamlit • Designed for enterprise security
                    </p>
                    <p style="margin: 0.5rem 0; font-size: 0.8rem; color: var(--secondary-text);">
                        Re-engineered and modernized by AI Assistant
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    def render_minimal_footer(self):
        """Render a minimal footer for compact views"""
        st.markdown(f"""
            <div style="text-align: center; margin-top: 2rem; padding: 1rem; font-size: 0.8rem; color: var(--secondary-text);">
                Synapse-Lite v2.0.0 | © {datetime.now().year} | Bitcoin Fraud Detection System
            </div>
        """, unsafe_allow_html=True)