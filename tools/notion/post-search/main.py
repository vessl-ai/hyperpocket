import json
import os
import sys

from typing import Optional, Literal

import requests
from pydantic import BaseModel, Field

token = os.getenv('NOTION_TOKEN')

class NotionSearchRequest(BaseModel):
    query: str = Field(
        default="",
        description="The text that the API compares page and database titles against.",
        title="Query"
    )
    filter: Optional[Literal['page', 'database']] = Field(
        default="",
        description="A set of criteria, value and property keys, that limits the results to either only pages or only databases."
    )
    sort_direction: Optional[Literal['ascending', 'descending']] = Field(
        default="",
        description="The direction to sort. Possible values include ascending and descending."
    )
    page_size: int = Field(
        default= 10,
        description="The number of items from the full list to include in the response. Maximum: 100.",
        title="Page Size"
    )
    start_cursor: Optional[str] = Field(
        default= "",
        description="A cursor value returned in a previous response that, if supplied, limits the response to results starting after the cursor. If not supplied, then the first page of results is returned.",
        title="Start Cursor"
    )

    
def notion_search(req: NotionSearchRequest):  
    body = dict()
    if req.query != "":
        body["query"] = req.query
    if req.filter != "":
        body["filter"] = {
            "value": req.filter,
            "property": "object"
        }
    if req.sort_direction != "":
        body["sort"] = {
            "direction": req.sort_direction,
            "timestamp": "last_edited_time"
        }
    body["page_size"] = req.page_size
    if req.start_cursor != "":
        body["start_cursor"] = req.start_cursor
    
    response = requests.post(
        url="https://api.notion.com/v1/search",
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
        },
        json = body,
    )

    if response.status_code != 200:
        return f"failed to insert calendar events. error : {response.text}"

    return response.json()

def main():
    req = json.load(sys.stdin.buffer)
    req_typed = NotionSearchRequest.model_validate(req)
    response = notion_search(req_typed)

    print(response)

if __name__ == '__main__':
    main()