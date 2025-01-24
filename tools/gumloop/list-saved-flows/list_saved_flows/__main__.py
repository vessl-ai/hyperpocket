import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv("GUMLOOP_TOKEN")
GUMLOOP_BASE_URL = "https://api.gumloop.com/api/v1"


class ListSavedFlowsRequest(BaseModel):
    user_id: Optional[str] = Field(default=None,
                                   description="The user ID to for which to list items. Required if project_id is not provided.")
    project_id: Optional[str] = Field(default=None,
                                      description="The project ID for which to list items. Required if user_id is not provided.")


def list_saved_flows(req: ListSavedFlowsRequest) -> dict:
    url = f"{GUMLOOP_BASE_URL}/list_saved_items"
    param = {
        "user_id": req.user_id,
        "project_id": req.project_id,
    }

    response = requests.get(url, params=param, headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = ListSavedFlowsRequest.model_validate(req)
    response = list_saved_flows(req_typed)

    print(response)


if __name__ == "__main__":
    main()
