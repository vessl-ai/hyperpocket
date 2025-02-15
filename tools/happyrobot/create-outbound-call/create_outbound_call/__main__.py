import json
import os
import sys
from typing import Any, Literal, Optional

import requests
from pydantic import BaseModel, Field


class CreateOutboundCallRequest(BaseModel):
    number_id: str = Field(
        ...,
        description="ID of the phone number that should trigger the call",
    )
    phone_number: str = Field(..., description="Phone number to call")
    prompt_id: Optional[str] = Field(
        None,
        description="ID of the prompt to use for the call. If empty, default outbound prompt will be used.",
    )
    use_case_id: Optional[str] = Field(
        None,
        description="ID of the use case that should handle the call",
    )
    agent_id: Optional[str] = Field(
        None,
        description="ID of the agent that should handle the call",
    )
    model_id: Optional[str] = Field(
        None,
        description="ID of the model that should handle the call",
    )
    language: Optional[
        Literal[
            "en-US",
            "en-GB",
            "es-MX",
            "es-ES",
            "es-CO",
            "pt-PT",
            "de-DE",
            "fr-FR",
            "pl-PL",
            "ro-RO",
            "it-IT",
            "zh-CN",
            "hi-IN",
            "ja-JP",
            "sv-SE",
        ]
    ] = Field(
        None,
        description="Language of the call. It will default to use case's default language",
    )
    params: Optional[dict[str, Any]] = Field(
        None,
        description="Dynamic parameters to inject into the templated use case prompt",
    )
    metadata: Optional[dict[str, Any]] = Field(
        None, description="Custom metadata associated with the call"
    )
    campaign_id: Optional[str] = Field(
        None,
        description="ID of the campaign that triggered the call",
    )
    scheduled_for: Optional[str] = Field(
        None,
        description="ISO 8601 UTC datetime the call is scheduled for. If not specified, the call will the executed immediately.",
    )
    max_duration_mins: Optional[int] = Field(
        None,
        description="Specifies the maximum duration of the call in minutes. This value takes precedence over the maximum duration specified in the use-case model. If neither is provided, the default duration is 10 minutes.",
    )


def create_outbound_call(req: CreateOutboundCallRequest):
    token = os.environ.get("HAPPYROBOT_TOKEN")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    data = req.model_dump(exclude_none=True)

    response = requests.post(
        "https://app.happyrobot.ai/api/v1/dial/outbound", headers=headers, json=data
    )

    if response.status_code != 200:
        raise Exception(f"Failed to create outbound call: {response.text}")

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = CreateOutboundCallRequest.model_validate(req)
    response = create_outbound_call(req_typed)
    print(json.dumps(response))


if __name__ == "__main__":
    main()
