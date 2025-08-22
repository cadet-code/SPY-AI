from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
import pickle
from typing import Optional
from core.config import settings

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.calendar_id = settings.google_calendar_id
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        try:
            # Check if we have valid credentials
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # If credentials are invalid or don't exist, get new ones
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    # For development, you can use a service account or OAuth2
                    # For now, we'll use a simplified approach
                    print("⚠️ Google Calendar authentication not configured")
                    print("To enable Google Calendar integration:")
                    print("1. Create a Google Cloud Project")
                    print("2. Enable Google Calendar API")
                    print("3. Create OAuth2 credentials")
                    print("4. Download credentials.json")
                    return
                
                # Save credentials for next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            print("✅ Google Calendar service initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Google Calendar: {e}")
            self.service = None
    
    async def add_appointment(self, client_name: str, service_name: str, 
                            appointment_datetime: datetime, duration_minutes: int,
                            client_email: str) -> Optional[str]:
        """Add appointment to Google Calendar"""
        
        if not self.service:
            print("⚠️ Google Calendar service not available")
            return None
        
        try:
            # Calculate end time
            end_time = appointment_datetime + timedelta(minutes=duration_minutes)
            
            # Create event
            event = {
                'summary': f'{service_name} - {client_name}',
                'description': f'Client: {client_name}\nService: {service_name}\nDuration: {duration_minutes} minutes\nEmail: {client_email}',
                'start': {
                    'dateTime': appointment_datetime.isoformat(),
                    'timeZone': 'America/New_York',  # Update with your timezone
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/New_York',  # Update with your timezone
                },
                'attendees': [
                    {'email': client_email},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 24 hours before
                        {'method': 'popup', 'minutes': 60},  # 1 hour before
                    ],
                },
                'colorId': '1',  # Blue color
            }
            
            # Insert event
            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                sendUpdates='all'  # Send email notifications to attendees
            ).execute()
            
            print(f"✅ Appointment added to Google Calendar: {event.get('htmlLink')}")
            return event.get('id')
            
        except Exception as e:
            print(f"❌ Error adding appointment to Google Calendar: {e}")
            return None
    
    async def update_appointment(self, event_id: str, client_name: str, service_name: str,
                               appointment_datetime: datetime, duration_minutes: int,
                               client_email: str) -> bool:
        """Update existing appointment in Google Calendar"""
        
        if not self.service:
            print("⚠️ Google Calendar service not available")
            return False
        
        try:
            # Calculate end time
            end_time = appointment_datetime + timedelta(minutes=duration_minutes)
            
            # Get existing event
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            
            # Update event details
            event['summary'] = f'{service_name} - {client_name}'
            event['description'] = f'Client: {client_name}\nService: {service_name}\nDuration: {duration_minutes} minutes\nEmail: {client_email}'
            event['start']['dateTime'] = appointment_datetime.isoformat()
            event['end']['dateTime'] = end_time.isoformat()
            
            # Update event
            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()
            
            print(f"✅ Appointment updated in Google Calendar: {updated_event.get('htmlLink')}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating appointment in Google Calendar: {e}")
            return False
    
    async def cancel_appointment(self, event_id: str) -> bool:
        """Cancel appointment in Google Calendar"""
        
        if not self.service:
            print("⚠️ Google Calendar service not available")
            return False
        
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            
            print(f"✅ Appointment cancelled in Google Calendar")
            return True
            
        except Exception as e:
            print(f"❌ Error cancelling appointment in Google Calendar: {e}")
            return False
    
    async def get_available_slots(self, date: datetime, duration_minutes: int) -> list:
        """Get available time slots for a specific date"""
        
        if not self.service:
            print("⚠️ Google Calendar service not available")
            return []
        
        try:
            # Get start and end of day
            start_of_day = date.replace(hour=9, minute=0, second=0, microsecond=0)
            end_of_day = date.replace(hour=20, minute=0, second=0, microsecond=0)
            
            # Get events for the day
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=start_of_day.isoformat(),
                timeMax=end_of_day.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Generate available slots
            available_slots = []
            current_time = start_of_day
            
            while current_time + timedelta(minutes=duration_minutes) <= end_of_day:
                slot_end = current_time + timedelta(minutes=duration_minutes)
                
                # Check if slot conflicts with any existing events
                slot_available = True
                for event in events:
                    event_start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    event_end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
                    
                    # Check for overlap
                    if (current_time < event_end and slot_end > event_start):
                        slot_available = False
                        break
                
                if slot_available:
                    available_slots.append(current_time.strftime('%H:%M'))
                
                # Move to next slot (15-minute intervals)
                current_time += timedelta(minutes=15)
            
            return available_slots
            
        except Exception as e:
            print(f"❌ Error getting available slots: {e}")
            return []

# Global Google Calendar service instance
calendar_service = GoogleCalendarService()

async def add_to_calendar(client_name: str, service_name: str, appointment_datetime: datetime,
                         duration_minutes: int, client_email: str) -> Optional[str]:
    """Add appointment to Google Calendar"""
    return await calendar_service.add_appointment(
        client_name, service_name, appointment_datetime, duration_minutes, client_email
    )

async def update_calendar_appointment(event_id: str, client_name: str, service_name: str,
                                    appointment_datetime: datetime, duration_minutes: int,
                                    client_email: str) -> bool:
    """Update appointment in Google Calendar"""
    return await calendar_service.update_appointment(
        event_id, client_name, service_name, appointment_datetime, duration_minutes, client_email
    )

async def cancel_calendar_appointment(event_id: str) -> bool:
    """Cancel appointment in Google Calendar"""
    return await calendar_service.cancel_appointment(event_id)

async def get_calendar_available_slots(date: datetime, duration_minutes: int) -> list:
    """Get available time slots from Google Calendar"""
    return await calendar_service.get_available_slots(date, duration_minutes)
