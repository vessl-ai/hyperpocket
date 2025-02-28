import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv("GOOGLE_TOKEN")


class GoogleListSpreadsheetRequest(BaseModel):
    pageSize: Optional[int] = Field(
        None,
        description="The maximum number of files to return per page. Partial or empty result pages are possible even before the end of the files list has been reached."
    )
    pageToken: Optional[str] = Field(
        None,
        description="The token for continuing a previous list request on the next page. This should be set to the value of 'nextPageToken' from the previous response."
    )


def list_spreadsheet(req: GoogleListSpreadsheetRequest):
    response = requests.get(
        url="https://www.googleapis.com/drive/v3/files",
        headers={
            "Authorization": f"Bearer {token}",
        },
        params={
            "q": "mimeType='application/vnd.google-apps.spreadsheet'",
            "pageSize": req.pageSize,
            "pageToken": req.pageToken,
        }
    )

    if response.status_code != 200:
        return f"failed to get spreadsheet list. error : {response.text}"

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleListSpreadsheetRequest.model_validate(req)
    response = list_spreadsheet(req_typed)

    print(response)


if __name__ == "__main__":
    main()
