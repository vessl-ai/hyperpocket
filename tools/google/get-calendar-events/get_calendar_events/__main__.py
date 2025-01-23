import json
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('GOOGLE_TOKEN')


class GoogleGetCalendarEventsRequest(BaseModel):
    calendar_id: str = Field(description="Google Calendar ID. The format should follow {user_name}@{domain}.")
    time_max: Optional[str] = Field(
        description="Upper bound (exclusive) for an event's start time to filter by. Optional. "
                    "The default is current time + 30 days. "
                    "Must be an RFC3339 timestamp with mandatory time zone offset, "
                    "for example, 2011-06-03T10:00:00-07:00, 2011-06-03T10:00:00Z. "
                    "Milliseconds may be provided but are ignored. "
                    "If timeMin is set, timeMax must be greater than timeMin.",
        default=(datetime.now() + timedelta(days=30)).isoformat(timespec='seconds') + "+00:00")
    time_min: Optional[str] = Field(
        description="Lower bound (exclusive) for an event's end time to filter by. "
                    "Optional. The default is current time"
                    "Must be an RFC3339 timestamp with mandatory time zone offset, "
                    "for example, 2011-06-03T10:00:00-07:00, 2011-06-03T10:00:00Z. "
                    "Milliseconds may be provided but are ignored. "
                    "If timeMax is set, timeMin must be smaller than timeMax.",
        default=datetime.now().isoformat(timespec='seconds') + "+00:00"
    )
    event_types: Optional[str] = Field(default="default", description="""
Event types to return. Optional. This parameter can be repeated multiple times to return events of different types. If unset, returns all event types.

Acceptable values are:
- "birthday": Special all-day events with an annual recurrence.
- "default": Regular events.
- "focusTime": Focus time events.
- "fromGmail": Events from Gmail.
- "outOfOffice": Out of office events.
- "workingLocation": Working location events.
""")
    max_results: int = Field(default=100, description="Maximum number of events returned on one result page.")


def get_calendar_events(req: GoogleGetCalendarEventsRequest):
    response = requests.get(
        url=f"https://www.googleapis.com/calendar/v3/calendars/{req.calendar_id}/events",
        params={
            "orderBy": "updated",
            "timeMin": req.time_min,
            "timeMax": req.time_max,
        },
        headers={
            "Authorization": f"Bearer {token}",
        }
    )

    if response.status_code != 200:
        return f"failed to get calendar events. error : {response.text}"

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleGetCalendarEventsRequest.model_validate(req)
    response = get_calendar_events(req_typed)

    print(response)


if __name__ == '__main__':
    main()
