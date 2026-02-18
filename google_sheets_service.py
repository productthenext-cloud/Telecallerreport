# google_sheets_integration.py
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import streamlit as st
import json

class GoogleSheetsService:
    def __init__(self):
        """Initialize Google Sheets service with credentials"""
        self.connect_to_sheets()
    
    def connect_to_sheets(self):
        """Connect to Google Sheets using credentials"""
        try:
            # Try to get credentials from Streamlit secrets
            if 'google_sheets' in st.secrets:
                credentials_dict = st.secrets["google_sheets"]
                scopes = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ]
                creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
                self.client = gspread.authorize(creds)
                
                # Open the spreadsheet
                if 'spreadsheet_id' in st.secrets["google_sheets"]:
                    self.spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
                    self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
                else:
                    self.spreadsheet = self.client.open("Telecaller Daily Reports")
                
                # Initialize worksheets
                self.init_worksheets()
            else:
                st.error("Google Sheets credentials not found in secrets")
                self.client = None
                self.spreadsheet = None
        except Exception as e:
            st.error(f"Error connecting to Google Sheets: {str(e)}")
            self.client = None
            self.spreadsheet = None
    
    def init_worksheets(self):
        """Initialize all required worksheets"""
        try:
            # Reports worksheet
            try:
                self.reports_ws = self.spreadsheet.worksheet("Reports")
            except:
                self.reports_ws = self.spreadsheet.add_worksheet("Reports", 1000, 20)
                # Add headers
                headers = ['Date', 'Telecaller', 'Day', 'Total Calls', 'New Data', 'CRM Data',
                          'Country Data', 'Fair Data', 'Video', 'Video Details', 
                          'Other Work Description', 'Visited Students', 'Remarks']
                self.reports_ws.append_row(headers)
            
            # Edit History worksheet
            try:
                self.edit_history_ws = self.spreadsheet.worksheet("EditHistory")
            except:
                self.edit_history_ws = self.spreadsheet.add_worksheet("EditHistory", 1000, 10)
                # Add headers
                headers = ['timestamp', 'user', 'username', 'role', 'action', 'report_date',
                          'telecaller', 'original_data', 'new_data']
                self.edit_history_ws.append_row(headers)
            
            # Users worksheet
            try:
                self.users_ws = self.spreadsheet.worksheet("Users")
            except:
                self.users_ws = self.spreadsheet.add_worksheet("Users", 100, 15)
                # Add headers
                headers = ['username', 'password', 'role', 'name', 'telecaller_name',
                          'permissions', 'created_at', 'updated_at', 'is_active']
                self.users_ws.append_row(headers)
                
        except Exception as e:
            st.error(f"Error initializing worksheets: {str(e)}")
    
    def get_sheet_names(self):
        """Get all worksheet names"""
        try:
            if self.spreadsheet:
                return [ws.title for ws in self.spreadsheet.worksheets()]
            return []
        except Exception as e:
            st.error(f"Error getting sheet names: {str(e)}")
            return []
    
    def get_all_reports(self):
        """Get all reports from Google Sheets"""
        try:
            if not self.spreadsheet:
                return pd.DataFrame()
            
            records = self.reports_ws.get_all_records()
            if records:
                df = pd.DataFrame(records)
                
                # Parse date
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
                
                # Convert numeric columns
                numeric_cols = ['Total Calls', 'New Data', 'CRM Data', 'Fair Data', 'Visited Students']
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                
                return df
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error fetching reports: {str(e)}")
            return pd.DataFrame()
    
    def add_report(self, report_data):
        """Add a new report to Google Sheets"""
        try:
            if not self.spreadsheet:
                return False
            
            # Prepare row data
            row = [
                report_data.get('date', ''),
                report_data.get('telecaller', ''),
                report_data.get('day', ''),
                report_data.get('total_calls', 0),
                report_data.get('new_data', 0),
                report_data.get('crm_data', 0),
                report_data.get('country_data', ''),
                report_data.get('fair_data', 0),
                report_data.get('video', 'No'),
                report_data.get('video_details', ''),
                report_data.get('other_work', ''),
                report_data.get('visited_students', 0),
                report_data.get('remarks', '')
            ]
            
            self.reports_ws.append_row(row)
            
            # Log the add action
            edit_log = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user': 'System',
                'username': 'system',
                'role': 'system',
                'action': 'ADD',
                'report_date': report_data.get('date', '').split()[0],
                'telecaller': report_data.get('telecaller', ''),
                'original_data': '',
                'new_data': json.dumps(report_data)
            }
            self.log_edit_action(edit_log)
            
            return True
        except Exception as e:
            st.error(f"Error adding report: {str(e)}")
            return False
    
    def update_report(self, index, report_data):
        """Update an existing report"""
        try:
            if not self.spreadsheet:
                return False
            
            # Get all records to find the row number
            records = self.reports_ws.get_all_records()
            if index >= len(records):
                return False
            
            # Row number in sheet (add 2 for header row and 1-indexing)
            row_num = index + 2
            
            # Prepare updated row
            updated_row = [
                report_data.get('date', ''),
                report_data.get('telecaller', ''),
                report_data.get('day', ''),
                report_data.get('total_calls', 0),
                report_data.get('new_data', 0),
                report_data.get('crm_data', 0),
                report_data.get('country_data', ''),
                report_data.get('fair_data', 0),
                report_data.get('video', 'No'),
                report_data.get('video_details', ''),
                report_data.get('other_work', ''),
                report_data.get('visited_students', 0),
                report_data.get('remarks', '')
            ]
            
            # Update each cell
            for col_num, value in enumerate(updated_row, start=1):
                self.reports_ws.update_cell(row_num, col_num, value)
            
            return True
        except Exception as e:
            st.error(f"Error updating report: {str(e)}")
            return False
    
    def delete_report(self, index):
        """Delete a report"""
        try:
            if not self.spreadsheet:
                return False
            
            # Row number in sheet (add 2 for header row and 1-indexing)
            row_num = index + 2
            self.reports_ws.delete_rows(row_num)
            return True
        except Exception as e:
            st.error(f"Error deleting report: {str(e)}")
            return False
    
    def log_edit_action(self, edit_log):
        """Log edit action to EditHistory worksheet"""
        try:
            if not self.spreadsheet:
                return False
            
            row = [
                edit_log.get('timestamp', ''),
                edit_log.get('user', ''),
                edit_log.get('username', ''),
                edit_log.get('role', ''),
                edit_log.get('action', ''),
                edit_log.get('report_date', ''),
                edit_log.get('telecaller', ''),
                str(edit_log.get('original_data', '')),
                str(edit_log.get('new_data', ''))
            ]
            
            self.edit_history_ws.append_row(row)
            return True
        except Exception as e:
            st.error(f"Error logging edit action: {str(e)}")
            return False
    
    def get_edit_logs(self):
        """Get all edit history logs"""
        try:
            if not self.spreadsheet:
                return pd.DataFrame()
            
            records = self.edit_history_ws.get_all_records()
            if records:
                df = pd.DataFrame(records)
                
                # Parse timestamp
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                
                return df.sort_values('timestamp', ascending=False)
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error fetching edit logs: {str(e)}")
            return pd.DataFrame()
    
    def get_users(self):
        """Get all users from Google Sheets"""
        try:
            if not self.spreadsheet:
                return {}
            
            records = self.users_ws.get_all_records()
            if records:
                users = {}
                for record in records:
                    username = record.get('username', '')
                    if username:
                        # Parse permissions JSON
                        permissions = {}
                        if record.get('permissions'):
                            try:
                                permissions = json.loads(record['permissions'])
                            except:
                                permissions = {}
                        
                        users[username] = {
                            'password': record.get('password', ''),
                            'role': record.get('role', 'telecaller'),
                            'name': record.get('name', ''),
                            'telecaller_name': record.get('telecaller_name', None),
                            'permissions': permissions,
                            'created_at': record.get('created_at', ''),
                            'updated_at': record.get('updated_at', ''),
                            'is_active': record.get('is_active', 'TRUE') == 'TRUE'
                        }
                return users
            return {}
        except Exception as e:
            st.error(f"Error fetching users: {str(e)}")
            return {}
    
    def save_users(self, users):
        """Save users to Google Sheets"""
        try:
            if not self.spreadsheet:
                return False
            
            # Clear existing data
            self.users_ws.clear()
            
            # Add headers
            headers = ['username', 'password', 'role', 'name', 'telecaller_name',
                      'permissions', 'created_at', 'updated_at', 'is_active']
            self.users_ws.append_row(headers)
            
            # Add user data
            for username, user_data in users.items():
                row = [
                    username,
                    user_data.get('password', ''),
                    user_data.get('role', ''),
                    user_data.get('name', ''),
                    user_data.get('telecaller_name', ''),
                    json.dumps(user_data.get('permissions', {})),
                    user_data.get('created_at', ''),
                    user_data.get('updated_at', ''),
                    'TRUE' if user_data.get('is_active', True) else 'FALSE'
                ]
                self.users_ws.append_row(row)
            
            return True
        except Exception as e:
            st.error(f"Error saving users: {str(e)}")
            return False