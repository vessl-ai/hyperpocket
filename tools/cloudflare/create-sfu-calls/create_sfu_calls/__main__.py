import json
import os
import sys

from pydantic import BaseModel, Field
from cloudflare import Cloudflare

token = os.getenv('CLOUDFLARE_TOKEN')
account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
email = os.getenv('CLOUDFLARE_EMAIL')


class CreateSfuCallsRequest(BaseModel):
    name: str = Field(default="sfu-app", description="The name of sfu calls app")


def create_sfu_calls(req: CreateSfuCallsRequest):
    client = Cloudflare(
        api_email=email,
        api_key=token,
    )
    sfu = client.calls.sfu.create(
        account_id=account_id,
    )
    print(sfu.uid)
    return


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = CreateSfuCallsRequest.model_validate(req)
    response = create_sfu_calls(req_typed)

    print(response)


if __name__ == '__main__':
    main()