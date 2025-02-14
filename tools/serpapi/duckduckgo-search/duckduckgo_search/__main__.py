import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class DuckDuckGoSearchRequest(BaseModel):
    q: str = Field(..., description="Query term to search in DuckDuckGo")

    kl: Optional[str] = Field(None, description="Region code for localization (e.g., 'us-en', 'uk-en', 'fr-fr')")

    safe: Optional[int] = Field(-1, description="Filtering level for adult content (1: Strict, -1: Moderate, -2: Off)")
    df: Optional[str] = Field(None,
                              description="Filter results by date ('d', 'w', 'm', 'y' or custom format 'YYYY-MM-DD..YYYY-MM-DD')")

    start: Optional[int] = Field(0, ge=0, description="Result offset for pagination (default: 0)")

    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode")

    output: Optional[str] = Field("json", description="Output format: 'json' (default) or 'html'")


def duckduckgo_search(req: DuckDuckGoSearchRequest):
    default = {
        "engine": "duckduckgo",
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
    req_typed = DuckDuckGoSearchRequest.model_validate(req)
    response = duckduckgo_search(req_typed)

    print(response)


if __name__ == '__main__':
    main()