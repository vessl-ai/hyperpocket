import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv("GOOGLE_TOKEN")


class GoogleListGmailRequest(BaseModel):
    q: Optional[str] = Field(
        default=None,
        description="gmail query, see https://support.google.com/mail/answer/7190?hl=en",
    )


def list_gmail(q: Optional[str] = None):
    """
    List gmail with gmail query

    Args:
        q(str) : gmail query, see https://support.google.com/mail/answer/7190?hl=en
                 call get_gmail_query_definition to get the definition of gmail query

    """
    response = requests.get(
        url=f"https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers={
            "Authorization": f"Bearer {token}",
        },
        params={
            "q": q,
        },
    )

    if response.status_code != 200:
        return f"failed to get mail list. error : {response.text}"

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleListGmailRequest.model_validate(req)
    response = list_gmail(req_typed)

    print(response)


if __name__ == "__main__":
    main()
