import streamlit as st
import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import uuid
from datetime import datetime

class DataLayer:
    def __init__(self):
        # Initialize connection to Google Sheets
        self.spreadsheet_id = os.getenv('SPREADSHEET_ID', '')
        self.sheet_names = {
            'USERS': 'Gebruikers',
            'PRACTICES': 'Huisartsen',
            'CHECKS': 'Controles',
            'LOGS': 'Logs'
        }
        self.initialize_database()
    
    def initialize_database(self, force_reinit=False):
        """Initialize the database connection"""
        try:
            # Check if credentials exist
            if os.path.exists('google_credentials.json'):
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_name('google_credentials.json', scope)
                self.client = gspread.authorize(creds)
                
                # Get or create the spreadsheet
                if not self.spreadsheet_id:
                    # Create new spreadsheet
                    spreadsheet = self.client.create('Huisarts Check Database')
                    self.spreadsheet_id = spreadsheet.id
                    st.session_state['spreadsheet_id'] = self.spreadsheet_id
                    print(f"Created new spreadsheet with ID: {self.spreadsheet_id}")
                else:
                    # Try to open existing spreadsheet
                    try:
                        spreadsheet = self.client.open_by_key(self.spreadsheet_id)
                    except Exception as e:
                        print(f"Error opening spreadsheet: {e}")
                        # Create new spreadsheet if opening fails
                        spreadsheet = self.client.create('Huisarts Check Database')
                        self.spreadsheet_id = spreadsheet.id
                        st.session_state['spreadsheet_id'] = self.spreadsheet_id
                        print(f"Created new spreadsheet with ID: {self.spreadsheet_id}")
                
                # Initialize sheets if needed
                self.ensure_database_structure(spreadsheet)
                return True
            else:
                print("Google credentials file not found")
                return False
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False
    
    def ensure_database_structure(self, spreadsheet):
        """Ensure all required sheets exist with proper headers"""
        # User sheet
        self.ensure_sheet(spreadsheet, self.sheet_names['USERS'], [
            'userId', 'email', 'isActive', 'isAdmin', 'settings'
        ])
        
        # Practices sheet
        self.ensure_sheet(spreadsheet, self.sheet_names['PRACTICES'], [
            'practiceId', 'userId', 'name', 'websiteUrl', 'status', 
            'lastChecked', 'lastStatusChange', 'details'
        ])
        
        # Checks sheet
        self.ensure_sheet(spreadsheet, self.sheet_names['CHECKS'], [
            'checkId', 'practiceId', 'timestamp', 'status', 'previousStatus', 
            'details', 'notificationSent'
        ])
        
        # Logs sheet
        self.ensure_sheet(spreadsheet, self.sheet_names['LOGS'], [
            'timestamp', 'level', 'message', 'data'
        ])
    
    def ensure_sheet(self, spreadsheet, sheet_name, headers):
        """Ensure a sheet exists with the correct headers"""
        try:
            # Try to get the sheet
            sheet = spreadsheet.worksheet(sheet_name)
            # Check if headers are correct
            existing_headers = sheet.row_values(1)
            if existing_headers != headers:
                # Clear and set new headers
                sheet.clear()
                sheet.append_row(headers)
        except gspread.exceptions.WorksheetNotFound:
            # Create sheet if it doesn't exist
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1, cols=len(headers))
            sheet.append_row(headers)
    
    # User methods
    def get_user_by_email(self, email):
        """Get a user by email"""
        # For demonstration, returning mock data
        return {
            'userId': '12345',
            'email': email,
            'isActive': True,
            'isAdmin': False,
            'settings': {
                'emailNotifications': True,
                'notificationFrequency': 'immediately'
            }
        }
    
    def create_user(self, user):
        """Create a new user"""
        # Mock implementation
        return user
    
    def update_user(self, user_id, updates):
        """Update user fields"""
        # Mock implementation
        return {
            'userId': user_id,
            'email': 'user@example.com',
            'isActive': True,
            'isAdmin': False,
            'settings': updates.get('settings', {})
        }
    
    # Practice methods
    def get_practices_by_user(self, user_id):
        """Get all practices for a user"""
        # Mock implementation
        return [
            {
                'practiceId': '1',
                'userId': user_id,
                'name': 'Huisartsenpraktijk Centrum',
                'websiteUrl': 'https://www.huisartscentrum.nl',
                'status': 'NOT_ACCEPTING',
                'lastChecked': '2025-03-15T12:00:00Z',
                'lastStatusChange': '2025-03-10T09:30:00Z',
                'details': json.dumps({
                    'waitingList': True,
                    'conditions': ['Woonachtig in postcode gebied 1011-1018'],
                    'waitingTime': 'Ongeveer 6 maanden',
                    'contactInfo': 'info@huisartscentrum.nl'
                })
            },
            {
                'practiceId': '2',
                'userId': user_id,
                'name': 'Huisartspraktijk Zuid',
                'websiteUrl': 'https://www.huisartszuid.nl',
                'status': 'ACCEPTING',
                'lastChecked': '2025-03-16T10:15:00Z',
                'lastStatusChange': '2025-03-05T14:20:00Z',
                'details': json.dumps({
                    'waitingList': False,
                    'conditions': ['Alleen patiënten uit Amsterdam Zuid'],
                    'waitingTime': None,
                    'contactInfo': 'aanmelden@huisartszuid.nl'
                })
            }
        ]
    
    def get_practice_by_id(self, practice_id):
        """Get a practice by ID"""
        # Mock implementation
        return {
            'practiceId': practice_id,
            'userId': '12345',
            'name': 'Huisartsenpraktijk Centrum',
            'websiteUrl': 'https://www.huisartscentrum.nl',
            'status': 'NOT_ACCEPTING',
            'lastChecked': '2025-03-15T12:00:00Z',
            'lastStatusChange': '2025-03-10T09:30:00Z',
            'details': json.dumps({
                'waitingList': True,
                'conditions': ['Woonachtig in postcode gebied 1011-1018'],
                'waitingTime': 'Ongeveer 6 maanden',
                'contactInfo': 'info@huisartscentrum.nl'
            })
        }
    
    def create_practice(self, practice):
        """Create a new practice"""
        # Mock implementation
        return practice
    
    def update_practice(self, practice_id, updates):
        """Update practice fields"""
        # Mock implementation
        return {
            'practiceId': practice_id,
            'userId': '12345',
            'name': updates.get('name', 'Huisartsenpraktijk'),
            'websiteUrl': updates.get('websiteUrl', 'https://example.com'),
            'status': updates.get('status', 'UNKNOWN'),
            'lastChecked': updates.get('lastChecked', '2025-03-15T12:00:00Z'),
            'lastStatusChange': updates.get('lastStatusChange', '2025-03-10T09:30:00Z'),
            'details': updates.get('details', '{}')
        }
    
    def delete_practice(self, practice_id):
        """Delete a practice"""
        # Mock implementation
        return True