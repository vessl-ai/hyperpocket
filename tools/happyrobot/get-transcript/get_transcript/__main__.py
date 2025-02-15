import json
import os
import sys

import requests
from pydantic import BaseModel, Field


class GetTranscriptRequest(BaseModel):
    call_id: str = Field(..., description="ID of the call to get the transcript for")


def get_transcript(req: GetTranscriptRequest):
    token = os.environ.get("HAPPYROBOT_TOKEN")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.get(
        f"https://app.happyrobot.ai/api/v1/calls/{req.call_id}/transcript",
        headers=headers,
    )

    if response.status_code != 200:
        raise Exception(f"Failed to get transcript: {response.text}")

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GetTranscriptRequest.model_validate(req)
    response = get_transcript(req_typed)
    print(json.dumps(response))


if __name__ == "__main__":
    main()
