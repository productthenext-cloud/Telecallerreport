import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data_processor import DataProcessor
import time

# Page configuration
st.set_page_config(
    page_title="Telecaller Daily Report Dashboard",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data processor
@st.cache_resource
def get_data_processor():
    return DataProcessor()

processor = get_data_processor()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1976D2;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .stat-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 5px solid #1976D2;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1976D2;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .video-day {
        border-left-color: #F44336 !important;
    }
    
    .video-day .stat-number {
        color: #F44336;
    }
    
    .success-card {
        border-left-color: #4CAF50 !important;
    }
    
    .success-card .stat-number {
        color: #4CAF50;
    }
    
    .warning-card {
        border-left-color: #FF9800 !important;
    }
    
    .warning-card .stat-number {
        color: #FF9800;
    }
    
    .tab-content {
        padding: 1rem;
    }
    
    .report-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .report-table th {
        background-color: #f0f2f6;
        padding: 12px;
        text-align: left;
        font-weight: bold;
        color: #333;
    }
    
    .report-table td {
        padding: 12px;
        border-bottom: 1px solid #ddd;
    }
    
    .report-table tr:hover {
        background-color: #f5f5f5;
    }
    
    .badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: 600;
    }
    
    .badge-primary {
        background-color: #e3f2fd;
        color: #1976D2;
    }
    
    .badge-success {
        background-color: #e8f5e9;
        color: #4CAF50;
    }
    
    .badge-warning {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .badge-danger {
        background-color: #f8d7da;
        color: #721c24;
    }
    
    .date-range-btn {
        padding: 8px 16px;
        margin-right: 8px;
        border-radius: 5px;
        border: 1px solid #ddd;
        background-color: white;
        cursor: pointer;
    }
    
    .date-range-btn.active {
        background-color: #1976D2;
        color: white;
        border-color: #1976D2;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 📞 Telecaller Dashboard")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["Dashboard", "Daily Reports", "Add Report", "Analysis", "System Status"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### Quick Actions")
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    if st.button("⚙️ Setup System"):
        st.info("System setup functionality would be implemented here")
    
    st.markdown("---")
    
    # Info
    st.markdown("### System Info")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown(f"**Timezone:** {time.tzname[0]}")

# Main Content
if page == "Dashboard":
    # Header
    st.markdown('<h1 class="main-header">📊 Telecaller Performance Dashboard</h1>', unsafe_allow_html=True)
    
    # Date Range Selector
    col1, col2, col3, col4, col5 = st.columns(5)
    date_ranges = {
        "Today": "today",
        "Yesterday": "yesterday",
        "This Week": "week",
        "This Month": "month",
        "All Time": "all"
    }
    
    selected_range = "today"
    for i, (label, value) in enumerate(date_ranges.items()):
        if i == 0:
            if col1.button(label, key=f"range_{value}"):
                selected_range = value
        elif i == 1:
            if col2.button(label, key=f"range_{value}"):
                selected_range = value
        elif i == 2:
            if col3.button(label, key=f"range_{value}"):
                selected_range = value
        elif i == 3:
            if col4.button(label, key=f"range_{value}"):
                selected_range = value
        elif i == 4:
            if col5.button(label, key=f"range_{value}"):
                selected_range = value
    
    # Get dashboard stats
    stats = processor.get_dashboard_stats(selected_range)
    
    # Stats Cards - Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['total_calls']:,}</div>
            <div class="stat-label">Total Calls</div>
            <div style="font-size: 0.8rem; color: #666;">Avg: {stats['avg_calls_per_day']}/day</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card success-card">
            <div class="stat-number">{stats['new_data']:,}</div>
            <div class="stat-label">New Data</div>
            <div style="font-size: 0.8rem; color: #666;">Avg: {stats['avg_new_data_per_day']}/day</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card warning-card">
            <div class="stat-number">{stats['crm_data']:,}</div>
            <div class="stat-label">CRM Updates</div>
            <div style="font-size: 0.8rem; color: #666;">{stats['crm_completion_rate']}% of calls</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card video-day">
            <div class="stat-number">{stats['video_activities']}</div>
            <div class="stat-label">Video Activities</div>
            <div style="font-size: 0.8rem; color: #666;">{stats['video_activities']} days with video</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Stats Cards - Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['country_data']:,}</div>
            <div class="stat-label">Country Data</div>
            <div style="font-size: 0.8rem; color: #666;">International leads</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['fair_data']:,}</div>
            <div class="stat-label">Fair Leads</div>
            <div style="font-size: 0.8rem; color: #666;">Event leads</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{stats['visited_students']:,}</div>
            <div class="stat-label">Visited Students</div>
            <div style="font-size: 0.8rem; color: #666;">Student visits</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card success-card">
            <div class="stat-number">{stats['conversion_rate']}%</div>
            <div class="stat-label">Conversion Rate</div>
            <div style="font-size: 0.8rem; color: #666;">New Data / Total Calls</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts Section
    st.markdown("---")
    st.markdown("### 📈 Performance Charts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Weekly Summary Chart
        weekly_data = processor.get_weekly_summary()
        if weekly_data:
            df_weekly = pd.DataFrame(weekly_data)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_weekly['formatted_date'],
                y=df_weekly['total_calls'],
                name='Total Calls',
                marker_color='#1976D2'
            ))
            fig.add_trace(go.Bar(
                x=df_weekly['formatted_date'],
                y=df_weekly['new_data'],
                name='New Data',
                marker_color='#4CAF50'
            ))
            fig.update_layout(
                title='Last 7 Days Performance',
                barmode='group',
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Performance Trend Chart
        trend_data = processor.get_performance_trend(30)
        if trend_data:
            df_trend = pd.DataFrame(trend_data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_trend['date'],
                y=df_trend['total_calls'],
                name='Total Calls',
                line=dict(color='#1976D2', width=3),
                fill='tozeroy',
                fillcolor='rgba(25, 118, 210, 0.1)'
            ))
            fig.add_trace(go.Scatter(
                x=df_trend['date'],
                y=df_trend['new_data'],
                name='New Data',
                line=dict(color='#4CAF50', width=3),
                fill='tozeroy',
                fillcolor='rgba(76, 175, 80, 0.1)'
            ))
            fig.update_layout(
                title='30-Day Performance Trend',
                height=400,
                showlegend=True,
                xaxis_title='Date',
                yaxis_title='Count'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent Reports
    st.markdown("---")
    st.markdown("### 📋 Recent Daily Reports")
    
    reports = processor.get_all_reports()
    if not reports.empty:
        # Show last 5 reports
        recent_reports = reports.head(5)
        
        for _, report in recent_reports.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                date_str = report['Date'].strftime('%Y-%m-%d') if pd.notna(report['Date']) else 'Unknown Date'
                st.markdown(f"**{date_str}** - {report.get('Day', '')}")
                
                cols = st.columns(5)
                metrics = [
                    ('Total Calls', report.get('Total Calls', 0), '#1976D2'),
                    ('New Data', report.get('New Data', 0), '#4CAF50'),
                    ('CRM Data', report.get('CRM Data', 0), '#FF9800'),
                    ('Visited Students', report.get('Visited Students', 0), '#795548'),
                    ('Video', report.get('Video', 'No'), '#F44336' if report.get('Video') == 'Yes' else '#666')
                ]
                
                for i, (label, value, color) in enumerate(metrics):
                    cols[i].metric(label, value)
                
                if pd.notna(report.get('Other Work Description')):
                    st.markdown(f"**Other Work:** {report['Other Work Description']}")
            
            with col2:
                if report.get('Video') == 'Yes':
                    st.markdown('<span class="badge badge-danger">Video Day</span>', unsafe_allow_html=True)
                if pd.notna(report.get('Country Data')):
                    st.markdown(f"**Country:** {report['Country Data']}")
            
            st.markdown("---")
    else:
        st.info("No reports found. Add your first report from the 'Add Report' page.")

elif page == "Daily Reports":
    st.markdown('<h1 class="main-header">📋 Daily Reports</h1>', unsafe_allow_html=True)
    
    # Search and Filters
    with st.expander("🔍 Search & Filters", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            start_date = st.date_input("Start Date", 
                                      value=datetime.now() - timedelta(days=30))
        
        with col2:
            end_date = st.date_input("End Date", 
                                    value=datetime.now())
        
        with col3:
            video_filter = st.selectbox(
                "Video Filter",
                ["All", "Yes", "No"],
                index=0
            )
        
        with col4:
            search_term = st.text_input("Search", 
                                       placeholder="Search by country, work description...")
    
    # Apply filters
    filters = {}
    if start_date:
        filters['start_date'] = start_date
    if end_date:
        filters['end_date'] = end_date
    if video_filter != "All":
        filters['video'] = video_filter
    if search_term:
        filters['search'] = search_term
    
    # Get filtered reports
    reports = processor.get_all_reports(filters)
    
    # Reports count
    st.markdown(f"**Found {len(reports)} reports**")
    
    # Export button
    if not reports.empty:
        csv = reports.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"telecaller_reports_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    # Display reports table
    if not reports.empty:
        # Format date for display
        reports_display = reports.copy()
        reports_display['Date'] = reports_display['Date'].dt.strftime('%Y-%m-%d')
        
        # Show table
        st.dataframe(
            reports_display,
            use_container_width=True,
            column_config={
                "Total Calls": st.column_config.NumberColumn(format="%d"),
                "New Data": st.column_config.NumberColumn(format="%d"),
                "CRM Data": st.column_config.NumberColumn(format="%d"),
                "Fair Data": st.column_config.NumberColumn(format="%d"),
                "Visited Students": st.column_config.NumberColumn(format="%d"),
            }
        )
        
        # Edit/Delete buttons for each report
        st.markdown("### Report Actions")
        selected_report = st.selectbox(
            "Select a report to edit/delete",
            options=reports_display.index.tolist(),
            format_func=lambda x: f"{reports_display.loc[x, 'Date']} - {reports_display.loc[x, 'Total Calls']} calls"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ Edit Selected Report"):
                st.session_state['editing_report'] = selected_report
                st.rerun()
        
        with col2:
            if st.button("🗑️ Delete Selected Report"):
                if st.warning("Are you sure you want to delete this report?"):
                    # This would call processor.delete_report()
                    st.success("Report deleted successfully!")
                    st.rerun()
    else:
        st.info("No reports found. Add your first report from the 'Add Report' page.")

elif page == "Add Report":
    st.markdown('<h1 class="main-header">➕ Add Daily Report</h1>', unsafe_allow_html=True)
    
    with st.form("add_report_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            report_date = st.date_input("Date *", value=datetime.now())
            total_calls = st.number_input("Total Calls *", min_value=0, value=0)
            crm_data = st.number_input("CRM Data *", min_value=0, value=0)
        
        with col2:
            day = st.selectbox("Day", 
                              ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                              index=datetime.now().weekday())
            new_data = st.number_input("New Data *", min_value=0, value=0)
            fair_data = st.number_input("Fair Data", min_value=0, value=0)
        
        with col3:
            country_data = st.selectbox("Country Data",
                                       ["", "UK", "Australia", "Canada", "USA", "New Zealand", "Other"])
            video = st.selectbox("Video Activity *", ["No", "Yes"])
            visited_students = st.number_input("Visited Students", min_value=0, value=0)
        
        # Video Details (shown only if video is Yes)
        if video == "Yes":
            video_details = st.text_input("Video Details *", 
                                         placeholder="e.g., TikTok video, training video...")
        else:
            video_details = ""
        
        # Other Work Description
        other_work = st.text_area("Other Work Description",
                                 placeholder="e.g., Trained volunteers, helped Asmita mam, filtered rough sheet...")
        
        # Remarks
        remarks = st.text_area("Remarks / Notes",
                              placeholder="Any additional notes, observations, or comments...")
        
        # Submit button
        submitted = st.form_submit_button("💾 Save Report")
        
        if submitted:
            # Validation
            if total_calls == 0:
                st.error("Total Calls is required!")
            elif new_data == 0:
                st.error("New Data is required!")
            elif crm_data == 0:
                st.error("CRM Data is required!")
            elif video == "Yes" and not video_details:
                st.error("Video Details is required when Video Activity is 'Yes'!")
            else:
                # Prepare report data
                report_data = {
                    'date': report_date.strftime('%d/%m/%Y %H:%M:%S'),
                    'day': day,
                    'total_calls': total_calls,
                    'new_data': new_data,
                    'crm_data': crm_data,
                    'country_data': country_data,
                    'fair_data': fair_data,
                    'video': video,
                    'video_details': video_details,
                    'other_work': other_work,
                    'visited_students': visited_students,
                    'remarks': remarks
                }
                
                # Add to Google Sheets
                success = processor.gs_service.add_report(report_data)
                
                if success:
                    st.success("✅ Report added successfully!")
                    st.balloons()
                    
                    # Clear form
                    st.rerun()
                else:
                    st.error("Failed to add report. Please try again.")

elif page == "Analysis":
    st.markdown('<h1 class="main-header">📈 Performance Analysis</h1>', unsafe_allow_html=True)
    
    # Performance Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        period = st.selectbox("Analysis Period", 
                             ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])
    
    with col2:
        metric = st.selectbox("Primary Metric",
                             ["Total Calls", "New Data", "Conversion Rate", "Video Activities"])
    
    with col3:
        grouping = st.selectbox("Group By",
                               ["Daily", "Weekly", "Monthly"])
    
    # Charts
    tab1, tab2, tab3 = st.tabs(["Trend Analysis", "Video Activities", "Country Distribution"])
    
    with tab1:
        # Trend Analysis
        if period == "Last 7 Days":
            trend_data = processor.get_performance_trend(7)
        elif period == "Last 30 Days":
            trend_data = processor.get_performance_trend(30)
        elif period == "Last 90 Days":
            trend_data = processor.get_performance_trend(90)
        else:
            trend_data = processor.get_performance_trend(365)
        
        if trend_data:
            df_trend = pd.DataFrame(trend_data)
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=df_trend['date'], y=df_trend['total_calls'], 
                          name="Total Calls", line=dict(color='blue')),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(x=df_trend['date'], y=df_trend['new_data'], 
                          name="New Data", line=dict(color='green')),
                secondary_y=True,
            )
            
            fig.update_layout(
                title=f"Performance Trend - {period}",
                height=500,
                showlegend=True
            )
            
            fig.update_yaxes(title_text="Total Calls", secondary_y=False)
            fig.update_yaxes(title_text="New Data", secondary_y=True)
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Video Activities
        video_activities = processor.get_video_activities(20)
        
        if video_activities:
            df_video = pd.DataFrame(video_activities)
            
            fig = px.bar(df_video, 
                        x='formatted_date', 
                        y='total_calls',
                        title="Video Activities Timeline",
                        labels={'formatted_date': 'Date', 'total_calls': 'Total Calls'},
                        color='new_data',
                        color_continuous_scale='Viridis')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Video Activities List
            st.markdown("### Recent Video Activities")
            for activity in video_activities[:10]:
                with st.expander(f"{activity['formatted_date']} - {activity['video_details']}"):
                    st.markdown(f"**Total Calls:** {activity['total_calls']}")
                    st.markdown(f"**New Data:** {activity['new_data']}")
                    if activity['other_work']:
                        st.markdown(f"**Other Work:** {activity['other_work']}")
        else:
            st.info("No video activities recorded.")
    
    with tab3:
        # Country Distribution
        country_dist = processor.get_country_distribution()
        
        if country_dist:
            df_country = pd.DataFrame(list(country_dist.items()), 
                                     columns=['Country', 'Count'])
            
            fig = px.pie(df_country, 
                        values='Count', 
                        names='Country',
                        title="Country Data Distribution",
                        hole=0.3)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Country Table
            st.markdown("### Country-wise Summary")
            st.dataframe(df_country.sort_values('Count', ascending=False), 
                        use_container_width=True)
        else:
            st.info("No country data available.")

elif page == "System Status":
    st.markdown('<h1 class="main-header">⚙️ System Status</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Connection Status")
        
        try:
            # Test connection
            sheet_names = processor.gs_service.get_sheet_names()
            
            if sheet_names:
                st.success("✅ Connected to Google Sheets")
                
                # Show available sheets
                st.markdown("#### Available Sheets:")
                for sheet in sheet_names:
                    st.markdown(f"- {sheet}")
                
                # Get report count
                reports = processor.get_all_reports()
                st.metric("Total Reports", len(reports))
            else:
                st.error("❌ No sheets found")
        
        except Exception as e:
            st.error(f"❌ Connection Error: {str(e)}")
    
    with col2:
        st.markdown("### Data Health")
        
        reports = processor.get_all_reports()
        
        if not reports.empty:
            # Data quality metrics
            total_records = len(reports)
            complete_records = reports.notna().all(axis=1).sum()
            video_records = reports[reports['Video'] == 'Yes'].shape[0]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Records", total_records)
            col2.metric("Complete Records", complete_records)
            col3.metric("Video Activities", video_records)
            
            # Data range
            if 'Date' in reports.columns and not reports['Date'].isna().all():
                min_date = reports['Date'].min()
                max_date = reports['Date'].max()
                st.markdown(f"**Data Range:** {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
            
            # Missing data analysis
            st.markdown("#### Missing Data Analysis")
            missing_data = reports.isnull().sum()
            missing_df = pd.DataFrame({
                'Column': missing_data.index,
                'Missing Values': missing_data.values,
                'Percentage': (missing_data.values / len(reports) * 100).round(1)
            })
            missing_df = missing_df[missing_df['Missing Values'] > 0]
            
            if not missing_df.empty:
                st.dataframe(missing_df, use_container_width=True)
            else:
                st.success("✅ No missing data found!")
        else:
            st.info("No data available for analysis")
    
    # System Actions
    st.markdown("---")
    st.markdown("### System Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh All Data"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("📊 Rebuild Charts"):
            st.rerun()
    
    with col3:
        if st.button("🧹 Clear Cache"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Cache cleared!")
            time.sleep(1)
            st.rerun()
    
    # Data Export
    st.markdown("---")
    st.markdown("### Data Export")
    
    reports = processor.get_all_reports()
    if not reports.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV Export
            csv = reports.to_csv(index=False)
            st.download_button(
                label="📥 Export All Data (CSV)",
                data=csv,
                file_name=f"telecaller_full_export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # JSON Export
            json_data = reports.to_json(orient='records', date_format='iso')
            st.download_button(
                label="📥 Export All Data (JSON)",
                data=json_data,
                file_name=f"telecaller_full_export_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )