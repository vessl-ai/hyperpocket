import json
import os
import sys
from pydantic import BaseModel
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])


class SlackPostMessageRequest(BaseModel):
    channel: str
    text: str


def post_message(req: SlackPostMessageRequest):
    try:
        client.chat_postMessage(channel=req.channel, text=req.text)
        print("Message posted successfully.")
    except SlackApiError as e:
        print(f"Failed to post message(error: {e.response['error']})")


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = SlackPostMessageRequest.model_validate(req)
    post_message(req_typed)


if __name__ == '__main__':
    main()
