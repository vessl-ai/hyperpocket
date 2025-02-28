import json
import os
import sys
import requests
from pydantic import BaseModel, Field

token = os.getenv('GOOGLE_TOKEN')


class GoogleCreateSpreadsheetRequest(BaseModel):
    title: str = Field(description="The title of the new spreadsheet.")


def create_spreadsheet(req: GoogleCreateSpreadsheetRequest):
    response = requests.post(
        url="https://sheets.googleapis.com/v4/spreadsheets",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "properties": {
                "title": req.title
            }
        }
    )

    if response.status_code != 200:
        return f"Failed to create spreadsheet. Error: {response.text}"

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleCreateSpreadsheetRequest.model_validate(req)
    response = create_spreadsheet(req_typed)

    print(response)


if __name__ == '__main__':
    main() 