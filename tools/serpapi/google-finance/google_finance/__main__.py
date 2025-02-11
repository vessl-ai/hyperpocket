import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class GoogleFinanceRequest(BaseModel):
    q: str = Field(...,
                   description="Query term for Google Finance search. Can be a stock, index, mutual fund, currency, or futures.")

    hl: Optional[str] = Field(None, description="Language code for localization (e.g., 'en', 'es', 'fr').")

    window: Optional[str] = Field("1D",
                                  description="Time range for the graph (Options: '1D', '5D', '1M', '6M', 'YTD', '1Y', '5Y', 'MAX'). Default: '1D'.")

    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format: 'json' (default) or 'html'.")


def google_finance(req: GoogleFinanceRequest):
    default = {
        "engine": "google_finance",
        "api_key": token
    }
    params = req.model_dump()
    params.update(default)

    response = requests.get(SERPAPI_URL, params=params)
    if response.status_code != 200:
        return f"failed to call serpapi. error: {response.text}"

    results = response.json()
    return results


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleFinanceRequest.model_validate(req)
    response = google_finance(req_typed)

    print(response)


if __name__ == '__main__':
    main()
