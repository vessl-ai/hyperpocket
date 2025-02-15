import json
import os
import sys

import requests
from pydantic import BaseModel, Field


class StopCallRequest(BaseModel):
    call_id: str = Field(..., description="ID of the call to stop")


def stop_call(req: StopCallRequest):
    token = os.environ.get("HAPPYROBOT_TOKEN")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.post(
        f"https://app.happyrobot.ai/api/v1/calls/{req.call_id}/stop", headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Failed to stop call: {response.text}")

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = StopCallRequest.model_validate(req)
    response = stop_call(req_typed)
    print(json.dumps(response))


if __name__ == "__main__":
    main()
