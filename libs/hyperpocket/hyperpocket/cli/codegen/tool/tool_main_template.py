from jinja2 import Template


def get_tool_main_template() -> Template:
    return Template('''import json
import os
import sys

from pydantic import BaseModel, Field

token = os.getenv('AUTH_PROVIDER_TOKEN')


class {{ capitalized_tool_name }}Request(BaseModel):
    param_1: str = Field(description="")


def {{ tool_name }}(req: {{ capitalized_tool_name }}Request):
    """
    Example of tool function
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
    """
    return


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = {{ capitalized_tool_name }}Request.model_validate(req)
    response = {{ tool_name }}(req_typed)

    print(response)


if __name__ == '__main__':
    main()
''')
