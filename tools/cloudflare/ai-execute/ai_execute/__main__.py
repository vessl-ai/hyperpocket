import json
import os
import sys

from pydantic import BaseModel, Field
import requests

token = os.getenv('CLOUDFLARE_TOKEN')
account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
model_name = os.getenv('CLOUDFLARE_MODEL_NAME')


class AiExecuteRequest(BaseModel):
    messages: list = Field(default="", description="Input messages to the AI model")

def ai_execute(req: AiExecuteRequest):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model_name}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.post(url, 
                             headers=headers, 
                             json={
                                 "messages": req.messages,
                             })

    if response.status_code != 200:
        return f"Failed to execute AI model. Error: {response.text}"

    return f"Successfully executed AI model. Response: {response.json()}"


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = AiExecuteRequest.model_validate(req)
    response = ai_execute(req_typed)

    print(response)


if __name__ == '__main__':
    main()