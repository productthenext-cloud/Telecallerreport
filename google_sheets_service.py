import gspread
from google.oauth2.service_account import Credentials
from config import SPREADSHEET_ID, CREDENTIALS_FILE
import pandas as pd
from datetime import datetime

class GoogleSheetsService:
    def __init__(self):
        self.scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE, 
            scopes=self.scope
        )
        self.client = gspread.authorize(self.credentials)
        self.sheet = self.client.open_by_key(SPREADSHEET_ID)
    
    def get_sheet_data(self, sheet_name='DailyReports'):
        """Get all data from a specific sheet"""
        try:
            worksheet = self.sheet.worksheet(sheet_name)
            data = worksheet.get_all_values()
            return data
        except Exception as e:
            print(f"Error getting sheet data: {e}")
            return []
    
    def get_data_as_dataframe(self, sheet_name='DailyReports'):
        """Get sheet data as pandas DataFrame"""
        try:
            worksheet = self.sheet.worksheet(sheet_name)
            data = worksheet.get_all_values()
            
            if len(data) <= 1:
                return pd.DataFrame()
            
            # First row as headers
            headers = data[0]
            rows = data[1:]
            
            df = pd.DataFrame(rows, columns=headers)
            
            # Clean and convert data types
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d/%m/%Y %H:%M:%S')
            
            # Convert numeric columns
            numeric_columns = ['Total Calls', 'New Data', 'CRM Data', 'Fair Data', 'Visited Students']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            return df
        except Exception as e:
            print(f"Error getting DataFrame: {e}")
            return pd.DataFrame()
    
    def add_report(self, report_data, sheet_name='DailyReports'):
        """Add a new report to the sheet"""
        try:
            worksheet = self.sheet.worksheet(sheet_name)
            
            # Prepare row data
            row_data = [
                report_data.get('date', ''),
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
                report_data.get('remarks', ''),
                datetime.now().strftime('%d/%m/%Y %H:%M:%S'),  # Created At
                datetime.now().strftime('%d/%m/%Y %H:%M:%S')   # Updated At
            ]
            
            worksheet.append_row(row_data)
            return True
        except Exception as e:
            print(f"Error adding report: {e}")
            return False
    
    def update_report(self, row_index, updates, sheet_name='DailyReports'):
        """Update an existing report"""
        try:
            worksheet = self.sheet.worksheet(sheet_name)
            
            # Column mapping
            column_map = {
                'Date': 1,
                'Day': 2,
                'Total Calls': 3,
                'New Data': 4,
                'CRM Data': 5,
                'Country Data': 6,
                'Fair Data': 7,
                'Video': 8,
                'Video Details': 9,
                'Other Work Description': 10,
                'Visited Students': 11,
                'Remarks': 12,
                'Updated At': 14
            }
            
            # Update specific cells
            for field, value in updates.items():
                if field in column_map:
                    col = column_map[field]
                    worksheet.update_cell(row_index, col, value)
            
            # Update Updated At
            worksheet.update_cell(row_index, column_map['Updated At'], 
                                 datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            return True
        except Exception as e:
            print(f"Error updating report: {e}")
            return False
    
    def delete_report(self, row_index, sheet_name='DailyReports'):
        """Delete a report"""
        try:
            worksheet = self.sheet.worksheet(sheet_name)
            worksheet.delete_rows(row_index)
            return True
        except Exception as e:
            print(f"Error deleting report: {e}")
            return False
    
    def get_sheet_names(self):
        """Get all sheet names in the spreadsheet"""
        try:
            worksheets = self.sheet.worksheets()
            return [ws.title for ws in worksheets]
        except Exception as e:
            print(f"Error getting sheet names: {e}")
            return []