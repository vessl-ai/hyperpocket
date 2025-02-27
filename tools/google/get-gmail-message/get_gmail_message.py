import base64
import json
import os
import sys

import requests
from pydantic import BaseModel, Field

token = os.getenv("GOOGLE_TOKEN")


class GoogleGetGmailMessageRequest(BaseModel):
    id: str = Field(
        description="The ID of the message to retrieve. This ID is usually retrieved using messages.list."
    )


def get_message_body(parts):
    body_content = []
    for part in parts:
        if part.get('parts'):
            nested_body_content = get_message_body(part['parts'])
            body_content.extend(nested_body_content)

        elif part.get('mimeType') == 'text/plain':
            body = part['body']['data']
            decoded_body = base64.urlsafe_b64decode(body).decode('utf-8')
            body_content.append({
                "partId": part['partId'],
                "filename": part["filename"],
                "body": decoded_body,
            })

    return body_content


def get_gmail_message(req: GoogleGetGmailMessageRequest):
    response = requests.get(
        url=f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{req.id}",
        headers={
            "Authorization": f"Bearer {token}",
        }
    )

    if response.status_code != 200:
        return f"failed to get a mail. error : {response.text}"

    message_data = response.json()
    payload = message_data['payload']
    full_headers = payload.get('headers', [])

    headers = []
    for header_name in full_headers:
        if header_name in ["Delivered-To", "Received", "Date", "From", "Mime-Version", "Message-ID", "Subject", "To"]:
            headers.append(header_name)

    body = get_message_body(payload.get('parts', []))

    return {
        "headers": headers,
        "body": body,
    }


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleGetGmailMessageRequest.model_validate(req)
    response = get_gmail_message(req_typed)

    print(response)


if __name__ == "__main__":
    main()
