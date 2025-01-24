import json
import os
import sys

from typing import Optional, List

import requests
from pydantic import BaseModel, Field

token = os.getenv('CALENDLY_TOKEN')


class CalendlyCreateOneOffEventTypeRequest(BaseModel):
    name: str = Field(default="", description="Calendly Event type name. It should be less than 56 characters.")
    co_hosts: Optional[List[str]] = Field(default=None, description="Calendly co-host user url list. ex) https://api.calendly.com/users/BBBB")
    duration: int = Field(default=30, description="Calendly Event duration in minutes.")
    timezone: str = Field(default="America/New_York", description="Calendly Event timezone. ex) America/New_York")
    date_setting_type: str = Field(default="date_range", description="Calendly Event date setting type.")
    date_setting_start_date: str = Field(default="2020-01-07", description="Calendly Event date setting start date. Format: YYYY-MM-DD")
    date_setting_end_date: str = Field(default="2020-01-08", description="Calendly Event date setting end date. Format: YYYY-MM-DD")
    location_kind: str = Field(default="physical", description="Calendly Event location kind.")
    location: Optional[str] = Field(default="WeWork", description="Calendly Event location.")
    location_additional_info: Optional[str] = Field(default=None, description="Calendly Event location additional info.")

def calendly_create_one_off_event_type(req: CalendlyCreateOneOffEventTypeRequest):
    current_host = get_current_host()
    
    response = requests.post(
        url="https://api.calendly.com/one_off_event_types",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": req.name,
            "host": current_host,
            "co_hosts": req.co_hosts,
            "duration": req.duration,
            "timezone": req.timezone,
            "date_setting": {
                "type": req.date_setting_type,
                "start_date": req.date_setting_start_date,
                "end_date": req.date_setting_end_date,
            },
            "location": {
                "kind": req.location_kind,
                "location": req.location,
                "additional_info": req.location_additional_info,
            },
        }
    )

    if response.status_code != 200:
        return f"failed to insert calendar events. error : {response.text}"

    return response.json()

def get_current_host():
    resp = requests.get(
        url = "https://api.calendly.com/users/me",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
    )
    if resp.status_code != 200:
        raise Exception(f"failed to authenticate. status_code : {resp.status_code}")
    return resp.json()['resource']['uri']
    

def main():
    req = json.load(sys.stdin.buffer)
    req_typed = CalendlyCreateOneOffEventTypeRequest.model_validate(req)
    response = calendly_create_one_off_event_type(req_typed)

    print(response)


if __name__ == '__main__':
    main()
