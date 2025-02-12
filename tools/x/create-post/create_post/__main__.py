import json
import os
import sys
import traceback
from typing import Optional, List

from pydantic import BaseModel, Field
import requests

X_API_ENDPOINT = "https://api.x.com/2/tweets"


class XGeo(BaseModel):
    place_id: Optional[str] = Field(
        None,
        description="A place in the world.",
    )


class XMedia(BaseModel):
    media_ids: List[str] = Field(
        ...,
        description="A list of Media Ids to be attached to a created Tweet.",
    )
    tagged_user_ids: Optional[List[str]] = Field(
        None,
        description="A list of User Ids to be tagged in the media for created Tweet.",
    )


class XPoll(BaseModel):
    duration_minutes: int = Field(
        ..., description="Duration of the poll in minutes, 5 < x < 10080"
    )
    options: List[str] = Field(..., description="List of options for the poll.")
    reply_settings: Optional[str] = Field(
        None,
        description="Settings to indicate who can reply to the Tweet. One of 'following', 'mentionedUsers'",
    )


class XCreatePostRequest(BaseModel):
    card_uri: Optional[str] = Field(
        None,
        description="Card Uri Parameter. This is mutually exclusive from Quote Tweet Id, Poll, Media, and Direct Message Deep Link.",
    )
    community_id: Optional[str] = Field(
        None,
        description="The unique identifier of this Community.",
    )
    direct_message_deep_link: Optional[str] = Field(
        None,
        description="Link to take the conversation from the public timeline to a private Direct Message.",
    )
    for_super_followers_only: Optional[bool] = Field(
        False,
        description="Exclusive Tweet for super followers.",
    )
    geo: Optional[XGeo] = Field(
        None,
        description="Place ID being attached to the Tweet for geo location.",
    )
    media: Optional[XMedia] = Field(
        None,
        description="Media information being attached to created Tweet. This is mutually exclusive from Quote Tweet Id, Poll, and Card URI.",
    )
    nullcast: Optional[bool] = Field(
        False,
        description="Nullcasted (promoted-only) Posts do not appear in the public timeline and are not served to followers.",
    )
    poll: Optional[XPoll] = Field(
        None,
        description="Poll options for a Tweet with a poll. This is mutually exclusive from Media, Quote Tweet Id, and Card URI.",
    )
    quote_tweet_id: Optional[str] = Field(
        None,
        description="Unique identifier of this Tweet. This is returned as a string in order to avoid complications with languages and tools that cannot handle large integers.",
    )
    text: str = Field(
        ...,
        description="The content of the Tweet.",
    )


def create_post(req: XCreatePostRequest):
    token = os.getenv("X_AUTH_TOKEN")

    payload = req.dict()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    try:
        response = requests.post(X_API_ENDPOINT, headers=headers, json=payload)

        return response.json()
    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return {"error": str(e)}


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = XCreatePostRequest.model_validate(req)

    response = create_post(req_typed)

    print(response)


if __name__ == "__main__":
    main()
