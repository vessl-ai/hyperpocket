import json
import os
import sys

from pydantic import BaseModel, Field

token = os.getenv('AUTH_PROVIDER_TOKEN')


class GetGraphGetPaperRequest(BaseModel):
    param_1: str = Field(description="")


def get_graph_get_paper(req: GetGraphGetPaperRequest):
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
    req_typed = GetGraphGetPaperRequest.model_validate(req)
    response = get_graph_get_paper(req_typed)

    print(response)


if __name__ == '__main__':
    main()