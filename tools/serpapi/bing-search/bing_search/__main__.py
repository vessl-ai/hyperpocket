import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class BingSearchRequest(BaseModel):
    q: str = Field(..., description="Search query including all Bing search operators")

    location: Optional[str] = Field(None, description="Location to originate search from")
    lat: Optional[float] = Field(None, description="GPS latitude for search origin")
    lon: Optional[float] = Field(None, description="GPS longitude for search origin")
    mkt: Optional[str] = Field(None, description="Market where the results come from (e.g., en-US)")

    cc: Optional[str] = Field(None, description="Country to search from (ISO 3166-1 format, e.g., 'us', 'de', 'gb')")

    first: Optional[int] = Field(1, ge=1, description="Offset of organic results (default: 1)")
    count: Optional[int] = Field(10, ge=1, le=50, description="Number of results per page (default: 10, max: 50)")

    safeSearch: Optional[str] = Field("Moderate",
                                      description="Filtering level for adult content ('Off', 'Moderate', 'Strict')")
    filters: Optional[str] = Field(None, description="Complex filtering options for results")

    device: Optional[str] = Field("desktop", description="Device type ('desktop', 'tablet', or 'mobile')")
    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode")

    output: Optional[str] = Field("json", description="Output format: 'json' (default) or 'html'")


def bing_search(req: BingSearchRequest):
    default = {
        "engine": "bing",
        "api_key": token
    }
    params = req.model_dump()
    params.update(default)

    response = requests.get(SERPAPI_URL, params=params)
    if response.status_code != 200:
        return f"failed to call serpapi. error: {response.text}"

    results = response.json()
    organic_results = results["organic_results"]
    return organic_results


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = BingSearchRequest.model_validate(req)
    response = bing_search(req_typed)

    print(response)


if __name__ == '__main__':
    main()
