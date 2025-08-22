from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime
import os
import pickle
from typing import Optional, List, Dict
from core.config import settings

# Google Sheets API scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetsService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.spreadsheet_id = settings.google_sheets_id
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            # Check if we have valid credentials
            if os.path.exists('sheets_token.pickle'):
                with open('sheets_token.pickle', 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # If credentials are invalid or don't exist, get new ones
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    # For development, you can use a service account or OAuth2
                    print("⚠️ Google Sheets authentication not configured")
                    print("To enable Google Sheets integration:")
                    print("1. Create a Google Cloud Project")
                    print("2. Enable Google Sheets API")
                    print("3. Create OAuth2 credentials")
                    print("4. Download credentials.json")
                    return
                
                # Save credentials for next run
                with open('sheets_token.pickle', 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=self.credentials)
            print("✅ Google Sheets service initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Google Sheets: {e}")
            self.service = None
    
    async def add_booking_to_sheet(self, booking) -> bool:
        """Add booking to Google Sheets tracking"""
        
        if not self.service or not self.spreadsheet_id:
            print("⚠️ Google Sheets service not available")
            return False
        
        try:
            # Prepare booking data
            booking_data = [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Timestamp
                booking.client_name,
                booking.client_email,
                booking.client_phone,
                booking.service_name,
                booking.appointment_date.strftime('%Y-%m-%d'),
                booking.appointment_time,
                f"{booking.service_duration} minutes",
                f"${booking.total_price:.2f}",
                booking.status,
                booking.confirmation_code if hasattr(booking, 'confirmation_code') else '',
                booking.special_requests or '',
                booking.google_calendar_event_id or ''
            ]
            
            # Append to sheet
            range_name = 'Bookings!A:M'  # Adjust range as needed
            body = {
                'values': [booking_data]
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            print(f"✅ Booking added to Google Sheets: {result.get('updates').get('updatedCells')} cells updated")
            return True
            
        except Exception as e:
            print(f"❌ Error adding booking to Google Sheets: {e}")
            return False
    
    async def create_spreadsheet_template(self) -> Optional[str]:
        """Create a new Google Sheets template for spa bookings"""
        
        if not self.service:
            print("⚠️ Google Sheets service not available")
            return None
        
        try:
            # Create new spreadsheet
            spreadsheet = {
                'properties': {
                    'title': f'{settings.spa_name} - Booking Tracker'
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Bookings',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 13
                            }
                        }
                    },
                    {
                        'properties': {
                            'title': 'Analytics',
                            'gridProperties': {
                                'rowCount': 100,
                                'columnCount': 10
                            }
                        }
                    }
                ]
            }
            
            spreadsheet = self.service.spreadsheets().create(body=spreadsheet).execute()
            spreadsheet_id = spreadsheet['spreadsheetId']
            
            # Add headers to Bookings sheet
            headers = [
                'Timestamp',
                'Client Name',
                'Client Email',
                'Client Phone',
                'Service',
                'Date',
                'Time',
                'Duration',
                'Price',
                'Status',
                'Confirmation Code',
                'Special Requests',
                'Calendar Event ID'
            ]
            
            header_range = 'Bookings!A1:M1'
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=header_range,
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
            # Format headers
            requests = [
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': 0.2,
                                    'green': 0.6,
                                    'blue': 0.8
                                },
                                'textFormat': {
                                    'bold': True,
                                    'foregroundColor': {
                                        'red': 1,
                                        'green': 1,
                                        'blue': 1
                                    }
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                }
            ]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
            print(f"✅ Created Google Sheets template: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
            return spreadsheet_id
            
        except Exception as e:
            print(f"❌ Error creating Google Sheets template: {e}")
            return None
    
    async def get_booking_analytics(self) -> Dict:
        """Get booking analytics from Google Sheets"""
        
        if not self.service or not self.spreadsheet_id:
            print("⚠️ Google Sheets service not available")
            return {}
        
        try:
            # Get all booking data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Bookings!A:M'
            ).execute()
            
            values = result.get('values', [])
            if len(values) <= 1:  # Only headers or empty
                return {}
            
            # Skip header row
            bookings = values[1:]
            
            # Calculate analytics
            total_bookings = len(bookings)
            total_revenue = sum(float(booking[8].replace('$', '')) for booking in bookings if booking[8] and '$' in booking[8])
            
            # Service breakdown
            services = {}
            for booking in bookings:
                service = booking[4] if len(booking) > 4 else 'Unknown'
                services[service] = services.get(service, 0) + 1
            
            # Status breakdown
            statuses = {}
            for booking in bookings:
                status = booking[9] if len(booking) > 9 else 'Unknown'
                statuses[status] = statuses.get(status, 0) + 1
            
            analytics = {
                'total_bookings': total_bookings,
                'total_revenue': total_revenue,
                'services': services,
                'statuses': statuses,
                'average_revenue_per_booking': total_revenue / total_bookings if total_bookings > 0 else 0
            }
            
            return analytics
            
        except Exception as e:
            print(f"❌ Error getting booking analytics: {e}")
            return {}
    
    async def update_booking_status(self, row_index: int, status: str) -> bool:
        """Update booking status in Google Sheets"""
        
        if not self.service or not self.spreadsheet_id:
            print("⚠️ Google Sheets service not available")
            return False
        
        try:
            range_name = f'Bookings!J{row_index + 2}'  # +2 because sheets are 1-indexed and we have headers
            body = {
                'values': [[status]]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ Booking status updated in Google Sheets")
            return True
            
        except Exception as e:
            print(f"❌ Error updating booking status: {e}")
            return False

# Global Google Sheets service instance
sheets_service = GoogleSheetsService()

async def add_booking_to_sheet(booking) -> bool:
    """Add booking to Google Sheets tracking"""
    return await sheets_service.add_booking_to_sheet(booking)

async def create_sheets_template() -> Optional[str]:
    """Create Google Sheets template"""
    return await sheets_service.create_spreadsheet_template()

async def get_booking_analytics() -> Dict:
    """Get booking analytics from Google Sheets"""
    return await sheets_service.get_booking_analytics()

async def update_booking_status_in_sheets(row_index: int, status: str) -> bool:
    """Update booking status in Google Sheets"""
    return await sheets_service.update_booking_status(row_index, status)
