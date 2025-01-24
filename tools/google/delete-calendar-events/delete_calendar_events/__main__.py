import json
import os
import sys

import requests
from pydantic import BaseModel, Field

token = os.getenv('GOOGLE_TOKEN')


class GoogleDeleteCalendarEventsRequest(BaseModel):
    calendar_id: str = Field(description="Google Calendar ID. The format should follow {user_name}@{domain}.")
    event_id: str = Field(description="Event id to be deleted")
    send_updates: str = Field(default="none", description="""Whether to send notifications about the creation of the new event. Note that some emails might still be sent. 
The default is none.
Acceptable values are:
- "all": Notifications are sent to all guests.
- "externalOnly": Notifications are sent to non-Google Calendar guests only.
- "none": No notifications are sent.
""")


def delete_calendar_events(req: GoogleDeleteCalendarEventsRequest):
    response = requests.delete(
        url=f"https://www.googleapis.com/calendar/v3/calendars/{req.calendar_id}/events/{req.event_id}",
        params={
            "sendUpdates": req.send_updates
        },
        headers={
            "Authorization": f"Bearer {token}",
        }
    )

    if response.status_code != 200:
        return f"failed to delete calendar events. error : {response.text}"

    return f"successfully deleted calendar events {req.event_id}"


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleDeleteCalendarEventsRequest.model_validate(req)
    response = delete_calendar_events(req_typed)

    print(response)


if __name__ == '__main__':
    main()
