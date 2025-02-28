import base64
import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv("GOOGLE_TOKEN")


class GoogleGetSpreadsheetRequest(BaseModel):
    spreadsheetId: str = Field(
        description="The spreadsheet to request."
    )
    ranges: Optional[list[str]] = Field(
        None,
        description="The ranges to retrieve from the spreadsheet."
    )
    includeGridData: Optional[bool] = Field(
        None,
        description="True if grid data should be returned. This parameter is ignored if a field mask was set in the request."
    )


def get_spreadsheet(req: GoogleGetSpreadsheetRequest):
    response = requests.get(
        url=f"https://sheets.googleapis.com/v4/spreadsheets/{req.spreadsheetId}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        params={
            "ranges": req.ranges,
            "includeGridData": req.includeGridData
        }
    )

    if response.status_code != 200:
        return f"failed to get spreadsheet. error : {response.text}"

    # Parse the response before returning
    return parse_spreadsheet_metadata(response.json())


def parse_spreadsheet_metadata(response):
    metadata = {
        'spreadsheet_id': response['spreadsheetId'],
        'title': response['properties']['title'],
        'locale': response['properties']['locale'],
        'timezone': response['properties']['timeZone'],
        'auto_recalc': response['properties']['autoRecalc'],
        'sheets': []
    }

    # Parse each sheet's metadata
    for sheet in response['sheets']:
        sheet_props = sheet['properties']
        sheet_data = {
            'sheet_id': sheet_props['sheetId'],
            'title': sheet_props['title'],
            'index': sheet_props['index'],
            'grid_properties': {
                'row_count': sheet_props['gridProperties']['rowCount'],
                'column_count': sheet_props['gridProperties']['columnCount']
            }
        }

        # Parse sheet data if available
        if 'data' in sheet:
            rows = []
            for row in sheet['data'][0]['rowData']:
                if 'values' in row:
                    row_values = []
                    for cell in row['values']:
                        if 'effectiveValue' in cell:
                            row_values.append(cell['effectiveValue'].get('stringValue', ''))
                        else:
                            row_values.append('')
                    rows.append(row_values)
            sheet_data['values'] = rows

        metadata['sheets'].append(sheet_data)

    return metadata


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleGetSpreadsheetRequest.model_validate(req)
    response = get_spreadsheet(req_typed)
    print(response)


if __name__ == "__main__":
    main()