import json
import os
import sys
from typing import Tuple, List

from pydantic import BaseModel, Field
from slack_sdk import WebClient

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN", ""))


class SlackGetMessageRequest(BaseModel):
    channel: str
    limit: int = Field(default=10)


def get_channel() -> List[Tuple[str, str]]:
    conversation_list = client.conversations_list(limit=500)
    channels = []
    for channel in conversation_list.get("channels", []):
        channels.append((channel["id"], channel["name"]))

    return channels


def get_channel_id_by_name(channel_name: str) -> str:
    channels = get_channel()
    for id, name in channels:
        if name == channel_name:
            return id


def get_messages(req: SlackGetMessageRequest):
    channel_id = get_channel_id_by_name(channel_name=req.channel)
    response = client.conversations_history(channel=channel_id, limit=req.limit)
    return response


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = SlackGetMessageRequest.model_validate(req)
    if req_typed.channel[0] == "#":
        req_typed.channel = req_typed.channel[1:]

    response = get_messages(req_typed)

    print(response)


if __name__ == '__main__':
    main()
