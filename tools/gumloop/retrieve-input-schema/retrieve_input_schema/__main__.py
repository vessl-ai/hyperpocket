import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv("GUMLOOP_TOKEN")

GUMLOOP_BASE_URL = "https://api.gumloop.com/api/v1"


class RetrieveInputSchemaRequest(BaseModel):
    saved_item_id: str = Field(
        description="The ID of the saved item for which to retrieve input schemas."
    )
    user_id: Optional[str] = Field(
        default=None,
        description="User ID that created the flow. Required if project_id is not provided."
    )
    project_id: Optional[str] = Field(
        default=None,
        description="Project ID that the flow is under. Required if user_id is not provided."
    )


def retrieve_input_schema(req: RetrieveInputSchemaRequest):
    url = f"{GUMLOOP_BASE_URL}/get_inputs"
    params = {
        "saved_item_id": req.saved_item_id,
        'user_id': req.user_id,
        "project_id": req.project_id,
    }
    response = requests.get(url=url, params=params, headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = RetrieveInputSchemaRequest.model_validate(req)
    response = retrieve_input_schema(req_typed)

    print(response)


if __name__ == '__main__':
    main()
