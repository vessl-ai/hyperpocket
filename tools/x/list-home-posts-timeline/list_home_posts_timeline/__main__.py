import json
import os
import sys
import traceback
from typing import Optional, List

from pydantic import BaseModel, Field
import requests

X_API_ENDPOINT = "https://api.x.com/2/users"


class XListUserPostRequest(BaseModel):
    id: str = Field(
        ...,
        description="The unique identifier of the user whose Tweets should be returned.",
    )


def list_home_posts(req: XListUserPostRequest):
    token = os.getenv("X_AUTH_TOKEN")

    headers = {
        "Authorization": f"Bearer {token}",
    }

    try:
        url = (
            X_API_ENDPOINT + f"/{req.id}/timelines/reverse_chronological",
        )  # TODO: add queryparams

        print(url)
        response = requests.get(
            headers=headers,
            url=url,
        )

        return response.json()
    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return {
            "error": str(e),
            "response_status": response.status_code,
            "response_text": response.text,
        }


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = XListUserPostRequest.model_validate(req)

    response = list_home_posts(req_typed)

    print(response)


if __name__ == "__main__":
    main()
