"""
Investigations Page for Synapse-Lite
Case management and investigation workflows
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

class InvestigationsPage:
    """Investigations page implementation"""
    
    def __init__(self, app_state):
        self.app_state = app_state
    
    def render(self):
        """Render the investigations page"""
        self._render_investigation_header()
        self._render_case_summary()
        self._render_case_management()
        self._render_investigation_tools()
    
    def _render_investigation_header(self):
        """Render investigations page header"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown("## 🔍 Investigation Management")
            st.markdown("Manage investigation cases, track evidence, and collaborate on complex fraud investigations")
        
        with col2:
            if st.button("📝 New Investigation", use_container_width=True):
                self._show_new_investigation_form()
        
        with col3:
            if st.button("📊 Generate Report", use_container_width=True):
                self._generate_investigation_report()
    
    def _render_case_summary(self):
        """Render investigation case summary"""
        from data.data_service import DataService
        data_service = DataService()
        cases = data_service.get_investigation_cases()
        
        # Calculate summary stats
        total_cases = len(cases)
        open_cases = len([c for c in cases if c.get('status') == 'open'])
        investigating = len([c for c in cases if c.get('status') == 'investigating'])
        closed_cases = len([c for c in cases if c.get('status') == 'closed'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Cases",
                total_cases,
                help="Total investigation cases"
            )
        
        with col2:
            st.metric(
                "Open Cases",
                open_cases,
                delta="⚠️" if open_cases > 5 else "✅",
                help="Cases awaiting investigation"
            )
        
        with col3:
            st.metric(
                "Active Investigations",
                investigating,
                help="Cases currently under investigation"
            )
        
        with col4:
            resolution_rate = (closed_cases / total_cases * 100) if total_cases > 0 else 0
            st.metric(
                "Resolution Rate",
                f"{resolution_rate:.1f}%",
                delta=f"{closed_cases} closed",
                help="Percentage of cases resolved"
            )
    
    def _render_case_management(self):
        """Render case management interface"""
        st.markdown("### 📋 Investigation Cases")
        
        # Filter controls
        with st.expander("🔍 Filter Cases", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                status_filter = st.selectbox(
                    "Status",
                    ["all", "open", "investigating", "pending_review", "closed", "escalated"]
                )
            
            with col2:
                priority_filter = st.selectbox(
                    "Priority",
                    ["all", "low", "medium", "high", "urgent"]
                )
            
            with col3:
                assignee_filter = st.selectbox(
                    "Assigned To",
                    ["all", "Analyst A", "Analyst B", "Senior Investigator", "Team Lead"]
                )
            
            with col4:
                time_filter = st.selectbox(
                    "Created",
                    ["all", "today", "this_week", "this_month", "older"]
                )
        
        # Get and filter cases
        from data.data_service import DataService
        data_service = DataService()
        cases = data_service.get_investigation_cases()
        
        filtered_cases = self._apply_case_filters(cases, status_filter, priority_filter, assignee_filter, time_filter)
        
        # Display cases
        if filtered_cases:
            # Case view tabs
            tab1, tab2 = st.tabs(["📊 Card View", "📋 Table View"])
            
            with tab1:
                self._render_case_cards(filtered_cases)
            
            with tab2:
                self._render_case_table(filtered_cases)
        else:
            st.info("No investigation cases match the current filters.")
    
    def _apply_case_filters(self, cases, status, priority, assignee, time_range):
        """Apply filters to investigation cases"""
        filtered = []
        
        for case in cases:
            # Status filter
            if status != "all" and case.get('status') != status:
                continue
            
            # Priority filter
            if priority != "all" and case.get('priority') != priority:
                continue
            
            # Assignee filter
            if assignee != "all" and case.get('assigned_to') != assignee:
                continue
            
            # Time filter
            if time_range != "all":
                created_date = datetime.fromisoformat(case.get('created_at', ''))
                now = datetime.now()
                
                if time_range == "today" and (now - created_date).days >= 1:
                    continue
                elif time_range == "this_week" and (now - created_date).days >= 7:
                    continue
                elif time_range == "this_month" and (now - created_date).days >= 30:
                    continue
                elif time_range == "older" and (now - created_date).days < 30:
                    continue
            
            filtered.append(case)
        
        return filtered
    
    def _render_case_cards(self, cases):
        """Render investigation cases as cards"""
        for i, case in enumerate(cases[:10]):  # Show first 10 cases
            priority = case.get('priority', 'medium')
            priority_colors = {
                'low': 'var(--info)',
                'medium': 'var(--warning)',
                'high': 'var(--error)',
                'urgent': 'var(--accent-red)'
            }
            
            status = case.get('status', 'open')
            status_icons = {
                'open': '🔓',
                'investigating': '🔍',
                'pending_review': '⏳',
                'closed': '✅',
                'escalated': '🚨'
            }
            
            created_date = datetime.fromisoformat(case.get('created_at', ''))
            days_ago = (datetime.now() - created_date).days
            
            with st.expander(f"{status_icons.get(status, '📋')} {case.get('title', 'Unknown Case')} - {priority.title()} Priority"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Case ID:** {case.get('id')}")
                    st.markdown(f"**Description:** {case.get('description', 'No description available')}")
                    st.markdown(f"**Related Addresses:** {len(case.get('related_addresses', []))}")
                    st.markdown(f"**Related Transactions:** {case.get('related_transactions', 0)}")
                    st.markdown(f"**Evidence Count:** {case.get('evidence_count', 0)}")
                    
                    # Tags
                    tags = case.get('tags', [])
                    if tags:
                        tag_html = " ".join([f'<span class="status-badge" style="background: var(--accent-blue); color: white; margin-right: 0.5rem;">{tag}</span>' for tag in tags])
                        st.markdown(f"**Tags:** {tag_html}", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**Status:** {status.replace('_', ' ').title()}")
                    st.markdown(f"**Priority:** {priority.title()}")
                    st.markdown(f"**Assigned To:** {case.get('assigned_to', 'Unassigned')}")
                    st.markdown(f"**Created:** {days_ago} days ago")
                    st.markdown(f"**Estimated Value:** ${case.get('estimated_amount_usd', 0):,.2f}")
                    
                    # Action buttons
                    if st.button(f"🔍 Investigate", key=f"investigate_case_{i}"):
                        self._open_case_details(case)
                    
                    if st.button(f"📝 Update", key=f"update_case_{i}"):
                        self._show_case_update_form(case)
    
    def _render_case_table(self, cases):
        """Render investigation cases as a table"""
        # Convert to DataFrame
        df_data = []
        for case in cases:
            created_date = datetime.fromisoformat(case.get('created_at', ''))
            df_data.append({
                'ID': case.get('id'),
                'Title': case.get('title', ''),
                'Status': case.get('status', '').replace('_', ' ').title(),
                'Priority': case.get('priority', '').title(),
                'Assigned To': case.get('assigned_to', 'Unassigned'),
                'Estimated Value': f"${case.get('estimated_amount_usd', 0):,.2f}",
                'Evidence': case.get('evidence_count', 0),
                'Created': created_date.strftime('%Y-%m-%d'),
                'Last Activity': case.get('last_activity', '')[:10] if case.get('last_activity') else 'N/A'
            })
        
        df = pd.DataFrame(df_data)
        
        # Display with selection
        selected_indices = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Show selected case details
        if selected_indices and len(selected_indices.selection.rows) > 0:
            selected_idx = selected_indices.selection.rows[0]
            selected_case = cases[selected_idx]
            self._render_case_details_sidebar(selected_case)
    
    def _render_case_details_sidebar(self, case):
        """Render case details in sidebar"""
        st.markdown("#### Case Details")
        
        # Basic information
        st.json({
            'ID': case.get('id'),
            'Title': case.get('title'),
            'Status': case.get('status'),
            'Priority': case.get('priority'),
            'Description': case.get('description'),
            'Assigned To': case.get('assigned_to'),
            'Estimated Amount': f"${case.get('estimated_amount_usd', 0):,.2f}",
            'Related Addresses': len(case.get('related_addresses', [])),
            'Related Transactions': case.get('related_transactions', 0),
            'Evidence Count': case.get('evidence_count', 0),
            'Tags': case.get('tags', [])
        })
        
        # Action buttons
        if st.button("🔍 Full Investigation View"):
            self._open_case_details(case)
        
        if st.button("📝 Update Case"):
            self._show_case_update_form(case)
        
        if st.button("📋 Add Evidence"):
            self._show_evidence_form(case)
    
    def _render_investigation_tools(self):
        """Render investigation tools and analytics"""
        st.markdown("### 🛠️ Investigation Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_case_analytics()
        
        with col2:
            self._render_investigation_workflow()
    
    def _render_case_analytics(self):
        """Render case analytics"""
        st.markdown("#### 📊 Case Analytics")
        
        from data.data_service import DataService
        data_service = DataService()
        cases = data_service.get_investigation_cases()
        
        # Status distribution
        status_counts = {}
        for case in cases:
            status = case.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        fig = px.pie(
            values=list(status_counts.values()),
            names=[s.replace('_', ' ').title() for s in status_counts.keys()],
            title="Case Status Distribution",
            color_discrete_map={
                'Open': '#ff9500',
                'Investigating': '#0052ff',
                'Pending Review': '#ffa502',
                'Closed': '#00d924',
                'Escalated': '#ff4757'
            }
        )
        
        fig.update_layout(
            template="plotly_dark" if self.app_state.get_setting('theme') == 'dark' else "plotly_white",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Priority breakdown
        priority_counts = {}
        for case in cases:
            priority = case.get('priority', 'unknown')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        st.markdown("**Priority Breakdown:**")
        for priority, count in priority_counts.items():
            st.markdown(f"- {priority.title()}: {count} cases")
    
    def _render_investigation_workflow(self):
        """Render investigation workflow"""
        st.markdown("#### 🔄 Investigation Workflow")
        
        workflow_steps = [
            "1. 🚨 Alert/Report received",
            "2. 📋 Case created and assigned",
            "3. 🔍 Initial investigation",
            "4. 📊 Evidence collection",
            "5. 🧩 Pattern analysis",
            "6. 👥 Collaboration/Review",
            "7. 📝 Report generation",
            "8. ✅ Case closure"
        ]
        
        for step in workflow_steps:
            st.markdown(step)
        
        st.markdown("---")
        
        # Investigation metrics
        st.markdown("**Investigation Metrics:**")
        st.metric("Avg Resolution Time", "4.2 days", "-0.8 days")
        st.metric("Evidence per Case", "12.3", "+2.1")
        st.metric("Collaboration Score", "8.7/10", "+0.3")
    
    def _show_new_investigation_form(self):
        """Show new investigation creation form"""
        st.markdown("#### 📝 Create New Investigation")
        
        with st.form("new_investigation"):
            title = st.text_input("Investigation Title", placeholder="Brief description of the case")
            description = st.text_area("Detailed Description", placeholder="Detailed description of the investigation...")
            
            col1, col2 = st.columns(2)
            with col1:
                priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"])
                assignee = st.selectbox("Assign To", ["Analyst A", "Analyst B", "Senior Investigator", "Team Lead"])
            
            with col2:
                estimated_value = st.number_input("Estimated Value (USD)", min_value=0.0, value=0.0)
                tags = st.text_input("Tags (comma-separated)", placeholder="aml, high-risk, mixer")
            
            submitted = st.form_submit_button("Create Investigation")
            
            if submitted and title:
                case_data = {
                    'title': title,
                    'description': description,
                    'priority': priority,
                    'assigned_to': assignee,
                    'estimated_amount_usd': estimated_value,
                    'tags': [tag.strip() for tag in tags.split(',') if tag.strip()]
                }
                
                new_case = self.app_state.add_investigation_case(case_data)
                st.success(f"Investigation case '{title}' created successfully!")
                st.rerun()
    
    def _show_case_update_form(self, case):
        """Show case update form"""
        st.markdown(f"#### 📝 Update Case: {case.get('title')}")
        st.info("Case update form would be implemented here")
    
    def _show_evidence_form(self, case):
        """Show evidence addition form"""
        st.markdown(f"#### 📋 Add Evidence to Case: {case.get('title')}")
        st.info("Evidence addition form would be implemented here")
    
    def _open_case_details(self, case):
        """Open detailed case view"""
        st.markdown(f"#### 🔍 Case Details: {case.get('title')}")
        st.info("Detailed case investigation view would be implemented here")
    
    def _generate_investigation_report(self):
        """Generate investigation report"""
        st.markdown("#### 📊 Investigation Report")
        st.info("Investigation report generation would be implemented here")