import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('GOOGLE_TOKEN')


class GoogleGetCalendarListRequest(BaseModel):
    pass


def get_calendar_list():
    response = requests.get(
        url=f"https://www.googleapis.com/calendar/v3/users/me/calendarList",
        headers={
            "Authorization": f"Bearer {token}",
        }
    )

    if response.status_code != 200:
        return f"failed to get calendar list. error : {response.text}"

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    response = get_calendar_list()

    print(response)


if __name__ == "__main__":
    main()
