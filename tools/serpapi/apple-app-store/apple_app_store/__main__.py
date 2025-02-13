import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class AppleAppStoreRequest(BaseModel):
    term: str = Field(..., description="Query term to search in the App Store")

    country: Optional[str] = Field("us", description="Country code for localization (e.g., 'us', 'uk', 'fr')")
    lang: Optional[str] = Field("en-us", description="Language code for localization (e.g., 'en-us', 'fr-fr', 'uk-ua')")

    num: Optional[int] = Field(10, ge=1, le=200, description="Number of results per page (1-200)")
    page: Optional[int] = Field(0, ge=0, description="Page number of the search results")

    disallow_explicit: Optional[bool] = Field(False, description="Filter explicit apps (default: False)")
    property: Optional[str] = Field("", description="Search property of an app (e.g., 'developer')")

    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode")

    output: Optional[str] = Field("json", description="Output format: 'json' (default) or 'html'")
    device: Optional[str] = Field("mobile", description="Device type: 'desktop', 'tablet', or 'mobile' (default)")


def apple_app_store(req: AppleAppStoreRequest):
    default = {
        "engine": "apple_app_store",
        "api_key": token,
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
    req_typed = AppleAppStoreRequest.model_validate(req)
    response = apple_app_store(req_typed)

    print(response)


if __name__ == '__main__':
    main()
