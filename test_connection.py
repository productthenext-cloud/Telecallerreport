import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Configuration
SPREADSHEET_ID = '1ybp4kG6_rVQobMn8o2C9VsNNttW5SfvX9HJxtrhNtrQ'  # Replace with your actual ID
CREDENTIALS_FILE = 'credentials.json'

def test_connection():
    print("🔍 Testing Google Sheets Connection...")
    print("=" * 50)
    
    try:
        # Authenticate
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials.from_service_account_file(
            CREDENTIALS_FILE, 
            scopes=scope
        )
        
        client = gspread.authorize(credentials)
        
        print("✅ Authentication successful!")
        
        # Open spreadsheet
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        print(f"✅ Spreadsheet opened: {spreadsheet.title}")
        
        # List sheets
        worksheets = spreadsheet.worksheets()
        print(f"📋 Available sheets:")
        for ws in worksheets:
            print(f"   - {ws.title} ({ws.row_count} rows × {ws.col_count} cols)")
        
        # Test reading DailyReports sheet
        print("\n📊 Testing DailyReports sheet...")
        try:
            daily_reports = spreadsheet.worksheet('DailyReports')
            data = daily_reports.get_all_values()
            
            if len(data) > 0:
                print(f"✅ DailyReports found with {len(data)} rows")
                print(f"   Headers: {data[0]}")
                
                if len(data) > 1:
                    print(f"   First data row: {data[1]}")
                    print(f"   Total rows with data: {len(data) - 1}")
                else:
                    print("   ⚠️ Sheet has headers but no data rows")
            else:
                print("   ⚠️ Sheet is empty")
                
        except Exception as e:
            print(f"❌ Error reading DailyReports: {str(e)}")
        
        # Check specific data
        print("\n🔍 Checking specific cells...")
        try:
            # Check cell A2 (first data row, first column)
            cell_value = daily_reports.acell('A2').value
            print(f"   A2 (Date): {cell_value}")
            
            # Check a few more cells
            for cell in ['B2', 'C2', 'D2', 'H2']:
                value = daily_reports.acell(cell).value
                print(f"   {cell}: {value}")
                
        except Exception as e:
            print(f"   ⚠️ Could not read specific cells: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Connection test COMPLETE!")
        print("\n📝 Summary:")
        print(f"   - Spreadsheet: {spreadsheet.title}")
        print(f"   - Sheets: {len(worksheets)}")
        print(f"   - DailyReports data rows: {len(data) - 1 if len(data) > 1 else 0}")
        
        return True
        
    except FileNotFoundError:
        print("❌ ERROR: credentials.json file not found!")
        print("   Make sure credentials.json is in the same folder")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Check if spreadsheet ID is correct")
        print("   2. Verify credentials.json file is valid")
        print("   3. Ensure Google Sheet is shared with service account")
        print("   4. Check internet connection")
        return False

if __name__ == "__main__":
    # First, let's check what's in the current directory
    import os
    print("📁 Current directory files:")
    for file in os.listdir('.'):
        print(f"   - {file}")
    print()
    
    # Run test
    success = test_connection()
    
    if success:
        print("\n🎉 READY TO RUN THE FULL APPLICATION!")
        print("Next command: streamlit run app.py")
    else:
        print("\n⚠️  Please fix the issues above before running the full app")