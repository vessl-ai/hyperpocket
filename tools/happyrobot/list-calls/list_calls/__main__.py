import json
import os
import sys
from typing import Literal, Optional

import requests
from pydantic import BaseModel, Field


class ListCallsRequest(BaseModel):
    type: Optional[Literal["Inbound", "Outbound"]] = Field(
        None, description="Filter by call type"
    )
    limit: Optional[int] = Field(None, description="Limit the number of calls returned")
    skip: Optional[int] = Field(None, description="Skip the first N calls")
    statuses: Optional[str] = Field(
        None, description="Filter by call statuses, comma separated"
    )
    tags: Optional[str] = Field(None, description="Filter by tags, comma separated")
    models: Optional[str] = Field(
        None, description="Filter by models names, comma separated"
    )
    ratings: Optional[str] = Field(
        None, description="Filter by ratings, comma separated"
    )
    use_cases: Optional[str] = Field(
        None, description="Filter by use case ids, comma separated"
    )
    from_: Optional[str] = Field(None, description="Filter by start date", alias="from")
    to: Optional[str] = Field(None, description="Filter by end date")
    sort: Optional[Literal["asc", "desc"]] = Field(None, description="Sort direction")
    search: Optional[str] = Field(
        None, description="Search by extraction or phone number"
    )
    campaigns: Optional[str] = Field(
        None, description="Filter by campaign ids, comma separated"
    )
    transfer_contact_email: Optional[str] = Field(
        None, description="Filter by transfer contact email"
    )


def list_calls(req: ListCallsRequest):
    token = os.environ.get("HAPPYROBOT_TOKEN")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    params = req.model_dump(exclude_none=True)

    response = requests.get(
        "https://app.happyrobot.ai/api/v1/calls", headers=headers, params=params
    )

    if response.status_code != 200:
        raise Exception(f"Failed to list calls: {response.text}")

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = ListCallsRequest.model_validate(req)
    response = list_calls(req_typed)
    print(json.dumps(response))


if __name__ == "__main__":
    main()
