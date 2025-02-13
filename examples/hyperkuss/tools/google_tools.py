from typing import Dict, Optional
from hyperpocket.tool import function_tool
from hyperpocket.auth import AuthProvider
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import logging
import os
import json

logger = logging.getLogger(__name__)

@function_tool(auth_provider=AuthProvider.GOOGLE)
def create_meet_link(
    title: str,
    duration_minutes: int = 60,
    **kwargs
) -> Dict:
    """
    Create a Google Meet link for a video conference.
    Args:
        title: Meeting title/description
        duration_minutes: Duration of meeting in minutes (default: 60)
    Returns:
        Meeting details including link and calendar event
    """
    try:
        # Get credentials from kwargs
        google_creds = kwargs.get("GOOGLE_CREDENTIALS")
        if not google_creds:
            raise ValueError("Google credentials not found")

        # Create credentials object from token
        creds = Credentials.from_authorized_user_info(json.loads(google_creds))

        # Create Calendar API service
        service = build('calendar', 'v3', credentials=creds)

        # Calculate start and end time
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(minutes=duration_minutes)

        # Create calendar event with Meet link
        event = {
            'summary': title,
            'description': f'Video conference for: {title}',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        # Insert the event with Meet details
        event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        # Extract Meet link and details
        meet_link = event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', '')
        
        return {
            "meet_link": meet_link,
            "event_id": event['id'],
            "title": title,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_minutes": duration_minutes,
            "calendar_link": event.get('htmlLink'),
            "message": f"Created Meet link: {meet_link}"
        }

    except Exception as e:
        logger.error(f"Failed to create Meet link: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to create Google Meet link"
        }

@function_tool(auth_provider=AuthProvider.GOOGLE)
def get_meetings(
    date_type: str = "today",  # "today", "tomorrow", "yesterday", or "custom"
    custom_date: Optional[str] = None,  # YYYY-MM-DD format for custom date
    max_results: int = 10,
    **kwargs
) -> Dict:
    """
    Get list of meetings from Google Calendar for a specific date.
    Args:
        date_type: Type of date to fetch ("today", "tomorrow", "yesterday", or "custom")
        custom_date: Specific date in YYYY-MM-DD format (required if date_type is "custom")
        max_results: Maximum number of meetings to return (default: 10)
    Returns:
        List of meetings with details for the specified date
    """
    try:
        # Get credentials from kwargs
        google_creds = kwargs.get("GOOGLE_CREDENTIALS")
        if not google_creds:
            raise ValueError("Google credentials not found")

        # Create credentials object from token
        creds = Credentials.from_authorized_user_info(json.loads(google_creds))

        # Create Calendar API service
        service = build('calendar', 'v3', credentials=creds)

        # Calculate target date
        today = datetime.datetime.now()
        if date_type == "tomorrow":
            target_date = today + datetime.timedelta(days=1)
        elif date_type == "yesterday":
            target_date = today - datetime.timedelta(days=1)
        elif date_type == "custom" and custom_date:
            try:
                target_date = datetime.datetime.strptime(custom_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid custom_date format. Use YYYY-MM-DD")
        else:  # today or invalid date_type
            target_date = today

        # Get date range for target date
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Get events for the target date
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_of_day.isoformat() + 'Z',
            timeMax=end_of_day.isoformat() + 'Z',
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Process events
        meetings = []
        for event in events:
            # Only include events with conferenceData (meetings)
            if 'conferenceData' in event:
                meeting_data = {
                    "title": event.get('summary', 'Untitled Meeting'),
                    "start_time": event['start'].get('dateTime', event['start'].get('date')),
                    "end_time": event['end'].get('dateTime', event['end'].get('date')),
                    "meet_link": event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', ''),
                    "organizer": event.get('organizer', {}).get('email'),
                    "attendees": [
                        attendee.get('email')
                        for attendee in event.get('attendees', [])
                    ],
                    "event_id": event['id'],
                    "calendar_link": event.get('htmlLink'),
                    "status": event.get('status', 'confirmed')
                }
                meetings.append(meeting_data)

        date_str = target_date.date().isoformat()
        date_desc = {
            "today": "today",
            "tomorrow": "tomorrow",
            "yesterday": "yesterday",
            "custom": f"on {date_str}"
        }.get(date_type, "today")

        return {
            "meetings": meetings,
            "count": len(meetings),
            "date": date_str,
            "message": f"Found {len(meetings)} meetings for {date_desc}"
        }

    except Exception as e:
        logger.error(f"Failed to fetch meetings: {str(e)}")
        return {
            "error": str(e),
            "message": f"Failed to fetch meetings"
        } 