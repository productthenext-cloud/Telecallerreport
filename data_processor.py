import pandas as pd
from datetime import datetime, timedelta
from google_sheets_service import GoogleSheetsService
import numpy as np

class DataProcessor:
    def __init__(self):
        self.gs_service = GoogleSheetsService()
    
    def get_all_reports(self, filters=None):
        """Get all reports with optional filtering"""
        df = self.gs_service.get_data_as_dataframe()
        
        if df.empty:
            return pd.DataFrame()
        
        # Apply filters
        if filters:
            if filters.get('start_date'):
                start_date = pd.to_datetime(filters['start_date'])
                df = df[df['Date'] >= start_date]
            
            if filters.get('end_date'):
                end_date = pd.to_datetime(filters['end_date'])
                df = df[df['Date'] <= end_date]
            
            if filters.get('video'):
                df = df[df['Video'] == filters['video']]
            
            if filters.get('search'):
                search_term = filters['search'].lower()
                search_columns = ['Country Data', 'Other Work Description', 'Video Details', 'Remarks', 'Day']
                mask = df[search_columns].apply(
                    lambda x: x.astype(str).str.lower().str.contains(search_term, na=False)
                ).any(axis=1)
                df = df[mask]
        
        # Sort by date (newest first)
        df = df.sort_values('Date', ascending=False)
        
        return df
    
    def get_dashboard_stats(self, date_range='all'):
        """Get statistics for dashboard"""
        df = self.gs_service.get_data_as_dataframe()
        
        if df.empty:
            return self._get_empty_stats()
        
        # Filter by date range
        now = datetime.now()
        
        if date_range == 'today':
            today = now.date()
            df = df[df['Date'].dt.date == today]
        elif date_range == 'yesterday':
            yesterday = (now - timedelta(days=1)).date()
            df = df[df['Date'].dt.date == yesterday]
        elif date_range == 'week':
            week_ago = (now - timedelta(days=7)).date()
            df = df[df['Date'].dt.date >= week_ago]
        elif date_range == 'month':
            month_ago = (now - timedelta(days=30)).date()
            df = df[df['Date'].dt.date >= month_ago]
        # 'all' includes all data
        
        # Calculate statistics
        stats = {
            'total_calls': df['Total Calls'].sum() if 'Total Calls' in df.columns else 0,
            'new_data': df['New Data'].sum() if 'New Data' in df.columns else 0,
            'crm_data': df['CRM Data'].sum() if 'CRM Data' in df.columns else 0,
            'country_data': df['Country Data'].count() if 'Country Data' in df.columns else 0,
            'fair_data': df['Fair Data'].sum() if 'Fair Data' in df.columns else 0,
            'visited_students': df['Visited Students'].sum() if 'Visited Students' in df.columns else 0,
            'video_activities': df[df['Video'] == 'Yes'].shape[0] if 'Video' in df.columns else 0,
            'total_days': df['Date'].dt.date.nunique() if not df.empty else 0,
        }
        
        # Calculate averages
        if stats['total_days'] > 0:
            stats['avg_calls_per_day'] = round(stats['total_calls'] / stats['total_days'], 1)
            stats['avg_new_data_per_day'] = round(stats['new_data'] / stats['total_days'], 1)
        else:
            stats['avg_calls_per_day'] = 0
            stats['avg_new_data_per_day'] = 0
        
        # Calculate conversion rate
        if stats['total_calls'] > 0:
            stats['conversion_rate'] = round((stats['new_data'] / stats['total_calls']) * 100, 1)
        else:
            stats['conversion_rate'] = 0
        
        # Calculate CRM completion rate
        if stats['total_calls'] > 0:
            stats['crm_completion_rate'] = round((stats['crm_data'] / stats['total_calls']) * 100, 1)
        else:
            stats['crm_completion_rate'] = 0
        
        return stats
    
    def get_weekly_summary(self, days=7):
        """Get weekly summary data"""
        df = self.gs_service.get_data_as_dataframe()
        
        if df.empty:
            return []
        
        # Filter last N days
        cutoff_date = datetime.now() - timedelta(days=days)
        df_recent = df[df['Date'] >= cutoff_date]
        
        if df_recent.empty:
            return []
        
        # Group by date
        df_recent['DateOnly'] = df_recent['Date'].dt.date
        
        summary = []
        for date in sorted(df_recent['DateOnly'].unique(), reverse=True)[:days]:
            day_data = df_recent[df_recent['DateOnly'] == date]
            
            summary.append({
                'date': date.strftime('%Y-%m-%d'),
                'formatted_date': date.strftime('%a, %b %d'),
                'total_calls': day_data['Total Calls'].sum(),
                'new_data': day_data['New Data'].sum(),
                'visited_students': day_data['Visited Students'].sum(),
                'video': 'Yes' if 'Yes' in day_data['Video'].values else 'No'
            })
        
        return summary
    
    def get_video_activities(self, limit=10):
        """Get recent video activities"""
        df = self.gs_service.get_data_as_dataframe()
        
        if df.empty:
            return []
        
        # Filter video activities
        video_df = df[df['Video'] == 'Yes'].copy()
        
        if video_df.empty:
            return []
        
        # Sort and limit
        video_df = video_df.sort_values('Date', ascending=False).head(limit)
        
        activities = []
        for _, row in video_df.iterrows():
            activities.append({
                'date': row['Date'].strftime('%Y-%m-%d') if pd.notna(row['Date']) else '',
                'formatted_date': row['Date'].strftime('%b %d, %Y') if pd.notna(row['Date']) else '',
                'video_details': row.get('Video Details', ''),
                'other_work': row.get('Other Work Description', ''),
                'total_calls': row.get('Total Calls', 0),
                'new_data': row.get('New Data', 0)
            })
        
        return activities
    
    def get_performance_trend(self, days=30):
        """Get performance trend data"""
        df = self.gs_service.get_data_as_dataframe()
        
        if df.empty:
            return []
        
        # Generate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        date_range = pd.date_range(start=start_date, end=end_date)
        
        trend_data = []
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            day_data = df[df['Date'].dt.date == date.date()]
            
            trend_data.append({
                'date': date_str,
                'formatted_date': date.strftime('%b %d'),
                'total_calls': day_data['Total Calls'].sum() if not day_data.empty else 0,
                'new_data': day_data['New Data'].sum() if not day_data.empty else 0,
                'visited_students': day_data['Visited Students'].sum() if not day_data.empty else 0
            })
        
        return trend_data
    
    def get_country_distribution(self):
        """Get country data distribution"""
        df = self.gs_service.get_data_as_dataframe()
        
        if df.empty or 'Country Data' not in df.columns:
            return {}
        
        country_counts = df['Country Data'].value_counts().to_dict()
        return country_counts
    
    def _get_empty_stats(self):
        """Return empty statistics dictionary"""
        return {
            'total_calls': 0,
            'new_data': 0,
            'crm_data': 0,
            'country_data': 0,
            'fair_data': 0,
            'visited_students': 0,
            'video_activities': 0,
            'total_days': 0,
            'avg_calls_per_day': 0,
            'avg_new_data_per_day': 0,
            'conversion_rate': 0,
            'crm_completion_rate': 0
        }