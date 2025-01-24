import json
import os
import sys
from typing import Optional, List

import requests
from pydantic import BaseModel, Field

token = os.getenv('GOOGLE_TOKEN')


class GoogleInsertCalendarEventsRequest(BaseModel):
    calendar_id: str = Field(description="Google Calendar ID. The format should follow {user_name}@{domain}.")
    send_updates: str = Field(default="none", description="""Whether to send notifications about the creation of the new event. Note that some emails might still be sent. 
The default is none.
Acceptable values are:
- "all": Notifications are sent to all guests.
- "externalOnly": Notifications are sent to non-Google Calendar guests only.
- "none": No notifications are sent.
""")
    summary: str = Field(description="event title summary.")
    description: Optional[str] = Field(default=None, description="event description.")
    start_datetime: str = Field(
        description="The time, as a combined date-time value (formatted according to RFC3339). A time zone offset is required unless a time zone is explicitly specified in timeZone.")
    end_datetime: str = Field(
        description="The time, as a combined date-time value (formatted according to RFC3339). A time zone offset is required unless a time zone is explicitly specified in timeZone.")

    attendees: List[str] = Field(default=[],
                                 description="attendees google calendar Id list. if you dont know this, should get google calendar list at first.")


def insert_calendar_events(req: GoogleInsertCalendarEventsRequest):
    response = requests.post(
        url=f"https://www.googleapis.com/calendar/v3/calendars/{req.calendar_id}/events",
        params={
            "sendUpdates": req.send_updates
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "summary": req.summary,
            "description": req.description,
            "start": {
                "dateTime": req.start_datetime
            },
            "end": {
                "dateTime": req.end_datetime
            },
            "attendees": [
                {
                    "email": attendee
                } for attendee in req.attendees
            ]
        }
    )

    if response.status_code != 200:
        return f"failed to insert calendar events. error : {response.text}"

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleInsertCalendarEventsRequest.model_validate(req)
    response = insert_calendar_events(req_typed)

    print(response)


if __name__ == '__main__':
    main()
