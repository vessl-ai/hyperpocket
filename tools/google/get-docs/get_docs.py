import json
import os
import sys
import requests
from pydantic import BaseModel, Field

token = os.getenv("GOOGLE_TOKEN")


class GoogleGetDocsRequest(BaseModel):
    url: str = Field(description="The url of the google doc to get the content of")


def get_docs(req: GoogleGetDocsRequest):
    docs_id = req.url.split("/d/")[1].split("/edit")[0]
    response = requests.get(
        url=f"https://docs.googleapis.com/v1/documents/{docs_id}",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    if response.status_code != 200:
        return f"Failed to get docs. Error: {response.text}"

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleGetDocsRequest.model_validate(req)
    response = get_docs(req_typed)

    print(response)


if __name__ == "__main__":
    main()
