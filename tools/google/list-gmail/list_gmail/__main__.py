import base64
import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv("GOOGLE_TOKEN")


class GoogleListGmailRequest(BaseModel):
    max_results: Optional[int] = Field(default=10,
                                       description="Maximum number of messages to return. This field must not exceed 10.")
    page_token: Optional[str] = Field(default=None,
                                      description="Page token to retrieve a specific page of results in the list.")
    q: Optional[str] = Field(
        default=None,
        description="""gmail query, Only return messages matching the specified query. Supports the same query format as the Gmail search box. For example, "from:someuser@example.com rfc822msgid:<somemsgid@example.com> is:unread". Parameter cannot be used when accessing the api using the gmail.metadata scope.""",
    )
    truncate_content: Optional[bool] = Field(default=True,
                                             description="Truncate the email body if it exceeds a certain length. default setting is true.")
    truncate_length: Optional[int] = Field(default=300, description="Truncated length of the email body. default length is 200.")


def get_message_body(parts, truncate_content, truncate_length):
    body_content = []
    for part in parts:
        if part.get('parts'):
            nested_body_content = get_message_body(part['parts'], truncate_content, truncate_length)
            body_content.extend(nested_body_content)

        elif part.get('mimeType') == 'text/plain':
            body = part['body']['data']
            decoded_body = base64.urlsafe_b64decode(body).decode('utf-8')
            if truncate_content and len(decoded_body) > truncate_length:
                decoded_body = decoded_body[:truncate_length] + "..."

            body_content.append({
                "partId": part['partId'],
                "filename": part["filename"],
                "body": decoded_body,
            })

    return body_content


def list_gmail(req: GoogleListGmailRequest):
    response = requests.get(
        url=f"https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers={
            "Authorization": f"Bearer {token}",
        },
        params={
            "maxResults": req.max_results,
            "q": req.q,
            "pageToken": req.page_token,
        },
    )

    if response.status_code != 200:
        return f"failed to get mail list. error : {response.text}"
    response_json = response.json()
    next_page_token = response_json.get("nextPageToken", None)
    result_size_estimate = response_json.get("resultSizeEstimate", None)
    message_id_list = response_json["messages"]

    messages = []
    for message_id in message_id_list:
        response = requests.get(
            url=f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id['id']}",
            headers={
                "Authorization": f"Bearer {token}",
            }
        )
        if response.status_code != 200:
            messages.append(f"failed to get a mail. error : {response.text}")
            continue

        message_data = response.json()
        payload = message_data['payload']
        full_headers = payload.get('headers', [])

        headers = []
        for header in full_headers:
            if header["name"] in ["Delivered-To", "Date", "From", "Subject", "To"]:
                headers.append(header)

        body = get_message_body(payload.get('parts', []), req.truncate_content, req.truncate_length)
        messages.append({
            "headers": headers,
            "body": body,
        })

    result = {
        "next_page_token": next_page_token,
        "result_size_estimate": result_size_estimate,
        "messages": messages,
    }

    return result


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleListGmailRequest.model_validate(req)
    response = list_gmail(req_typed)

    print(response)


if __name__ == "__main__":
    main()
