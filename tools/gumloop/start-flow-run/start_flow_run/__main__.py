import json
import os
import sys
from typing import Optional

from gumloop import GumloopClient
from pydantic import BaseModel, Field

token = os.getenv("GUMLOOP_TOKEN")
GUMLOOP_BASE_URL = "https://api.gumloop.com/api/v1"


class StartFlowRunRequest(BaseModel):
    saved_item_id: str = Field(description="The ID for the saved flow.")
    user_id: str = Field(description="The ID for the user initiating the flow.")
    pipeline_inputs: Optional[dict] = Field(
        default=None,
        description="A dict of inputs for the flow. you can get the pipeline_inputs schema of this run in `retrieve-input-schema`")
    project_id: Optional[str] = Field(default=None,
                                      description="The ID of the project within which the flow is executed. This is optional.")
    timeout: Optional[int] = Field(default=None, description="Maximum time to wait for flow completion (seconds)")


def start_flow_run(req: StartFlowRunRequest) -> dict:
    client = GumloopClient(
        api_key=token,
        user_id=req.user_id,
    )

    output = client.run_flow(
        flow_id=req.saved_item_id,
        inputs=req.pipeline_inputs,
        timeout=req.timeout
    )

    return output


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = StartFlowRunRequest.model_validate(req)
    response = start_flow_run(req_typed)

    print(response)


if __name__ == '__main__':
    main()
