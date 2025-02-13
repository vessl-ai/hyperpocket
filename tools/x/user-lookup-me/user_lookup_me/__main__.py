import json
import os
import sys
import traceback
from typing import Optional, List

from pydantic import BaseModel, Field
import requests

X_API_ENDPOINT = "https://api.x.com/2/users/me"


class XUserLookupMeRequest(BaseModel):
    user_fields: Optional[List[str]] = Field(
        None,
        description="A comma-separated list of fields to include in the response, Available options: affiliation, connection_status, created_at, description, entities, id, is_identity_verified, location, most_recent_tweet_id, name, parody, pinned_tweet_id, profile_banner_url, profile_image_url, protected, public_metrics, receives_your_dm, subscription, subscription_type, url, username, verified, verified_followers_count, verified_type, withheld",
    )


def user_lookup_me(req: XUserLookupMeRequest):
    token = os.getenv("X_AUTH_TOKEN")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    url_with_query = X_API_ENDPOINT
    if req.user_fields:
        url_with_query += f"?user.fields={','.join(req.user_fields)}"

    try:
        response = requests.get(
            X_API_ENDPOINT,
            headers=headers,
        )

        return response.json()
    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return {"error": str(e)}


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = XUserLookupMeRequest.model_validate(req)

    response = user_lookup_me(req_typed)

    print(response)


if __name__ == "__main__":
    main()
