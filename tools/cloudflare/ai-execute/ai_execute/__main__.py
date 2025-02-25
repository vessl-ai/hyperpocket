import json
import os
import sys

from pydantic import BaseModel, Field
import requests

token = os.getenv('CLOUDFLARE_TOKEN')
account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')


class AiExecuteRequest(BaseModel):
    model_name: str = Field(default="", description="The name of the AI model to execute")
    text: str = Field(default="", description="Input text to the AI model")

def ai_execute(req: AiExecuteRequest):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{req.model_name}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.post(url, 
                             headers=headers, 
                             json={
                                 "text": req.text
                             })

    if response.status_code != 200:
        return f"Failed to execute AI model. Error: {response.text}"

    return f"Successfully executed AI model. Response: {response.json()}"
    return


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = AiExecuteRequest.model_validate(req)
    response = ai_execute(req_typed)

    print(response)


if __name__ == '__main__':
    main()