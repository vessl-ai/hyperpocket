import json
import os
import sys
import requests
import re
from pydantic import BaseModel, Field

# Retrieve the Google API token from environment variables
token = os.getenv('GOOGLE_TOKEN')


class GoogleUpdateCellsRequest(BaseModel):
    spreadsheet_id: str = Field(description="The ID of the spreadsheet to update.")
    sheet_id: int = Field(
        description="The ID of the sheet to update. This can be retrieved from the spreadsheet object.")
    range: str = Field(description="The A1 notation of the range to update.")
    values: list = Field(description="The values to be entered into the spreadsheet.")


def a1_to_gridrange(a1_range: str):
    """
    Converts an A1 notation range into a GridRange format.
    """
    match = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", a1_range)
    if not match:
        raise ValueError("Invalid A1 notation.")

    start_col, start_row, end_col, end_row = match.groups()

    def col_to_index(col):
        """
        Converts a column letter (e.g., 'A', 'B', ..., 'Z', 'AA', etc.) to a zero-based column index.
        """
        expn = 0
        col = col[::-1]
        col_index = 0
        for i in range(len(col)):
            col_index += (ord(col[i]) - ord('A') + 1) * (26 ** expn)
            expn += 1
        return col_index - 1  # Convert to zero-based index

    return {
        "startRowIndex": int(start_row) - 1,  # Convert to zero-based index
        "endRowIndex": int(end_row),
        "startColumnIndex": col_to_index(start_col),
        "endColumnIndex": col_to_index(end_col) + 1  # The end index is exclusive, so add 1
    }


def update_cells(req: GoogleUpdateCellsRequest):
    grid_range = a1_to_gridrange(req.range)
    grid_range["sheetId"] = req.sheet_id

    response = requests.post(
        url=f"https://sheets.googleapis.com/v4/spreadsheets/{req.spreadsheet_id}:batchUpdate",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "requests": [
                {
                    "updateCells": {
                        "range": grid_range,
                        "rows": [
                            {"values": [{"userEnteredValue": {"stringValue": str(value)}} for value in row]}
                            for row in req.values
                        ],
                        "fields": "userEnteredValue"
                    }
                }
            ]
        }
    )

    if response.status_code != 200:
        return f"Failed to update cells. Error: {response.text}"

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleUpdateCellsRequest.model_validate(req)
    response = update_cells(req_typed)
    print(response)


if __name__ == '__main__':
    main()
