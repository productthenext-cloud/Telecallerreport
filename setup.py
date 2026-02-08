import os
import json
from pathlib import Path

def setup_environment():
    """Setup the environment and verify credentials"""
    
    print("=" * 60)
    print("Telecaller Daily Report Dashboard - Setup")
    print("=" * 60)
    
    # Check for credentials file
    credentials_file = "credentials.json"
    
    if not os.path.exists(credentials_file):
        print("\n❌ ERROR: credentials.json not found!")
        print("\nPlease follow these steps to create credentials:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Sheets API")
        print("4. Create Service Account credentials")
        print("5. Download JSON key file")
        print("6. Rename it to 'credentials.json' and place in this folder")
        print("\nThe file should contain your service account credentials.")
        return False
    
    # Check spreadsheet ID
    config_file = "config.py"
    if not os.path.exists(config_file):
        print("\n❌ ERROR: config.py not found!")
        print("\nCreating default config.py...")
        
        spreadsheet_id = input("\nEnter your Google Spreadsheet ID: ").strip()
        
        config_content = f'''import os
from pathlib import PathS

# Google Sheets Configuration
SPREADSHEET_ID = '{spreadsheet_id}'
SHEET_NAME = 'DailyReports'

# Service Account Credentials
CREDENTIALS_FILE = 'credentials.json'

# Application Settings
DATE_FORMAT = '%d/%m/%Y'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = f'{{DATE_FORMAT}} {{TIME_FORMAT}}'
'''
        
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        print("✅ config.py created successfully!")
    
    # Check if Google Sheet exists and has correct structure
    try:
        from google_sheets_service import GoogleSheetsService
        
        print("\n🔍 Testing connection to Google Sheets...")
        service = GoogleSheetsService()
        sheet_names = service.get_sheet_names()
        
        print(f"✅ Connected successfully!")
        print(f"📋 Available sheets: {', '.join(sheet_names)}")
        
        # Check for DailyReports sheet
        if 'DailyReports' not in sheet_names:
            print("\n⚠️  Warning: 'DailyReports' sheet not found!")
            create_sheet = input("Do you want to create it? (y/n): ").strip().lower()
            
            if create_sheet == 'y':
                # You would need to implement sheet creation
                print("Sheet creation would be implemented here...")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        return False

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    os.system("pip install -r requirements.txt")
    print("✅ Packages installed successfully!")

def run_application():
    """Run the Streamlit application"""
    print("\n🚀 Starting Telecaller Dashboard...")
    print("📊 Open your browser and go to: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application")
    os.system("streamlit run app.py")

if __name__ == "__main__":
    # Run setup
    if setup_environment():
        # Install requirements
        install_requirements()
        
        # Run application
        run_application()
    else:
        print("\n❌ Setup failed. Please fix the issues above.")