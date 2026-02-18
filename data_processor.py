# Add this at the top of your data_processor.py
import os
import json
import tempfile
from pathlib import Path

class DataProcessor:
    def __init__(self):
        # Determine if running on Render
        self.is_render = os.environ.get('RENDER', False)
        
        if self.is_render:
            # Use temp directory for storage on Render
            self.data_dir = Path(tempfile.gettempdir()) / 'telecaller_dashboard'
            self.data_dir.mkdir(exist_ok=True)
            
            # For Google Sheets credentials
            # Option 1: Use environment variable for credentials JSON
            if os.environ.get('GOOGLE_CREDENTIALS_JSON'):
                creds_path = self.data_dir / 'google_credentials.json'
                with open(creds_path, 'w') as f:
                    f.write(os.environ.get('GOOGLE_CREDENTIALS_JSON'))
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(creds_path)
        else:
            # Local development
            self.data_dir = Path('data')
            self.data_dir.mkdir(exist_ok=True)
        
        # Rest of your initialization...

# data_processor.py
import pandas as pd
from datetime import datetime, timedelta
from google_sheets_service import GoogleSheetsService
import streamlit as st
import json

class DataProcessor:
    def __init__(self):
        """Initialize the DataProcessor with Google Sheets integration"""
        self.gs_service = GoogleSheetsService()
    
    def add_report(self, report_data):
        """Add a new report"""
        try:
            return self.gs_service.add_report(report_data)
        except Exception as e:
            st.error(f"Error adding report: {str(e)}")
            return False
    
    def get_all_reports(self, filters=None):
        """Get all reports with optional filters"""
        try:
            df = self.gs_service.get_all_reports()
            
            if df.empty:
                return df
            
            # Convert Date column to datetime
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df = df.dropna(subset=['Date'])
            
            # Convert numeric columns
            numeric_cols = ['Total Calls', 'New Data', 'CRM Data', 'Fair Data', 'Visited Students']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            # Apply filters
            if filters:
                if 'start_date' in filters and filters['start_date']:
                    df = df[df['Date'].dt.date >= filters['start_date']]
                if 'end_date' in filters and filters['end_date']:
                    df = df[df['Date'].dt.date <= filters['end_date']]
                if 'telecaller' in filters and filters['telecaller'] and filters['telecaller'] != 'All':
                    df = df[df['Telecaller'] == filters['telecaller']]
                if 'video' in filters and filters['video'] != 'All':
                    df = df[df['Video'] == filters['video']]
                if 'search' in filters and filters['search']:
                    search_term = filters['search'].lower()
                    mask = df.astype(str).apply(lambda x: x.str.lower().str.contains(search_term, na=False)).any(axis=1)
                    df = df[mask]
            
            return df.sort_values('Date', ascending=False)
        except Exception as e:
            st.error(f"Error fetching reports: {str(e)}")
            return pd.DataFrame()
    
    def update_report(self, index, report_data):
        """Update an existing report"""
        try:
            return self.gs_service.update_report(index, report_data)
        except Exception as e:
            st.error(f"Error updating report: {str(e)}")
            return False
    
    def delete_report(self, index):
        """Delete a report"""
        try:
            return self.gs_service.delete_report(index)
        except Exception as e:
            st.error(f"Error deleting report: {str(e)}")
            return False
    
    def get_dashboard_stats(self, time_range='today', telecaller=None):
        """Get dashboard statistics"""
        df = self.get_all_reports()
        
        if df.empty:
            return {
                'total_calls': 0, 'new_data': 0, 'crm_data': 0, 'video_activities': 0,
                'country_data': 0, 'country_data_count': 0, 'fair_data': 0, 'visited_students': 0,
                'avg_calls_per_day': 0, 'avg_new_data_per_day': 0,
                'crm_completion_rate': 0, 'conversion_rate': 0
            }
        
        if telecaller:
            df = df[df['Telecaller'] == telecaller]
        
        today = datetime.now().date()
        
        if time_range == 'today':
            df = df[df['Date'].dt.date == today]
        elif time_range == 'yesterday':
            yesterday = today - timedelta(days=1)
            df = df[df['Date'].dt.date == yesterday]
        elif time_range == 'week':
            week_ago = today - timedelta(days=7)
            df = df[df['Date'].dt.date >= week_ago]
        elif time_range == 'month':
            month_ago = today - timedelta(days=30)
            df = df[df['Date'].dt.date >= month_ago]
        
        total_calls = df['Total Calls'].sum() if not df.empty else 0
        new_data = df['New Data'].sum() if not df.empty else 0
        crm_data = df['CRM Data'].sum() if not df.empty else 0
        video_activities = df[df['Video'] == 'Yes'].shape[0] if not df.empty else 0
        
        # Country data - count of non-empty country entries
        country_data_count = df['Country Data'].notna() & (df['Country Data'] != '') if not df.empty else 0
        country_data_count = country_data_count.sum() if not isinstance(country_data_count, int) else 0
        
        fair_data = df['Fair Data'].sum() if not df.empty else 0
        visited_students = df['Visited Students'].sum() if not df.empty else 0
        
        num_days = len(df['Date'].dt.date.unique()) if not df.empty else 1
        avg_calls_per_day = total_calls / num_days if num_days > 0 else 0
        avg_new_data_per_day = new_data / num_days if num_days > 0 else 0
        
        crm_completion_rate = (crm_data / total_calls * 100) if total_calls > 0 else 0
        conversion_rate = (new_data / total_calls * 100) if total_calls > 0 else 0
        
        return {
            'total_calls': total_calls,
            'new_data': new_data,
            'crm_data': crm_data,
            'video_activities': video_activities,
            'country_data': country_data_count,
            'country_data_count': country_data_count,
            'fair_data': fair_data,
            'visited_students': visited_students,
            'avg_calls_per_day': round(avg_calls_per_day, 1),
            'avg_new_data_per_day': round(avg_new_data_per_day, 1),
            'crm_completion_rate': round(crm_completion_rate, 1),
            'conversion_rate': round(conversion_rate, 1)
        }
    
    def get_weekly_summary(self, telecaller=None):
        """Get weekly performance summary"""
        df = self.get_all_reports()
        
        if df.empty:
            return []
        
        if telecaller:
            df = df[df['Telecaller'] == telecaller]
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        df_week = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        
        if df_week.empty:
            return []
        
        daily_stats = df_week.groupby(df_week['Date'].dt.date).agg({
            'Total Calls': 'sum',
            'New Data': 'sum'
        }).reset_index()
        
        daily_stats['date'] = pd.to_datetime(daily_stats['Date']).dt.strftime('%Y-%m-%d')
        daily_stats = daily_stats.sort_values('Date')
        
        return daily_stats.to_dict('records')
    
    def get_performance_trend(self, days=30, telecaller=None):
        """Get performance trend for specified number of days"""
        df = self.get_all_reports()
        
        if df.empty:
            return []
        
        if telecaller:
            df = df[df['Telecaller'] == telecaller]
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        df_trend = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
        
        if df_trend.empty:
            return []
        
        trend_data = df_trend.groupby(df_trend['Date'].dt.date).agg({
            'Total Calls': 'sum',
            'New Data': 'sum'
        }).reset_index()
        
        trend_data['date'] = pd.to_datetime(trend_data['Date']).dt.strftime('%Y-%m-%d')
        trend_data = trend_data.sort_values('Date')
        
        return trend_data.to_dict('records')
    
    def get_telecaller_performance(self):
        """Get performance summary for all telecallers"""
        df = self.get_all_reports()
        
        if df.empty or 'Telecaller' not in df.columns:
            return pd.DataFrame()
        
        performance = df.groupby('Telecaller').agg({
            'Total Calls': 'sum',
            'New Data': 'sum',
            'CRM Data': 'sum',
            'Video': lambda x: (x == 'Yes').sum()
        }).reset_index()
        
        performance.columns = ['Telecaller', 'Total Calls', 'New Data', 'CRM Data', 'Video Activities']
        performance['Conversion Rate'] = (performance['New Data'] / performance['Total Calls'] * 100).round(1)
        
        return performance
    
    def get_video_activities(self, days=30, telecaller=None):
        """Get video activities"""
        df = self.get_all_reports()
        
        if df.empty:
            return []
        
        if telecaller:
            df = df[df['Telecaller'] == telecaller]
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        video_df = df[(df['Video'] == 'Yes') & (df['Date'] >= start_date) & (df['Date'] <= end_date)].copy()
        
        if video_df.empty:
            return []
        
        video_df = video_df.sort_values('Date', ascending=False)
        video_df['date'] = video_df['Date'].dt.strftime('%Y-%m-%d')
        
        return video_df.to_dict('records')
    
    def get_country_distribution(self, telecaller=None):
        """Get country distribution of leads"""
        df = self.get_all_reports()
        
        if df.empty:
            return {}
        
        if telecaller:
            df = df[df['Telecaller'] == telecaller]
        
        country_data = df[df['Country Data'].notna() & (df['Country Data'] != '')]
        
        if country_data.empty:
            return {}
        
        return country_data['Country Data'].value_counts().to_dict()
    
    def log_edit_action(self, edit_log):
        """Log edit actions for history tracking"""
        try:
            return self.gs_service.log_edit_action(edit_log)
        except Exception as e:
            st.error(f"Error logging edit action: {str(e)}")
            return False
    
    def get_edit_logs(self):
        """Get edit history logs"""
        try:
            return self.gs_service.get_edit_logs()
        except Exception as e:
            st.error(f"Error fetching edit logs: {str(e)}")
            return pd.DataFrame()
    
    def check_connection(self):
        """Check connection status"""
        try:
            return self.gs_service.check_connection()
        except:
            return {'google_sheets': False, 'worksheets': [], 'local_mode': True}