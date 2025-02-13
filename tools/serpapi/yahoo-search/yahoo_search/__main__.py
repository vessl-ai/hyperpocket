import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class YahooSearchRequest(BaseModel):
    p: str = Field(..., description="Search query for Yahoo! Search.")

    yahoo_domain: Optional[str] = Field(None,
                                        description="Yahoo! domain to use (default: 'search.yahoo.com').")
    vc: Optional[str] = Field(None, description="Country code for Yahoo! search localization (e.g., 'us', 'uk', 'fr').")
    vl: Optional[str] = Field(None, description="Language restriction for Yahoo! search (e.g., 'lang_fr').")

    b: Optional[int] = Field(1, description="Pagination offset for results (default: 1).")

    vm: Optional[str] = Field(None,
                              description="Filtering level for adult content ('r': Strict, 'i': Moderate, 'p': Off).")
    vs: Optional[str] = Field(None, description="Filter results by top-level domains (e.g., '.com,.org').")
    vf: Optional[str] = Field(None, description="Specify file format to filter results (e.g., 'pdf', 'txt').")
    fr2: Optional[str] = Field(None, description="Rendering positions and expansions for some elements.")
    d: Optional[str] = Field(None, description="Destination parameter for related topics.")

    device: Optional[str] = Field("desktop", description="Device type ('desktop', 'tablet', 'mobile').")
    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format ('json' or 'html').")


def yahoo_search(req: YahooSearchRequest):
    default = {
        "engine": "yahoo",
        "api_key": token
    }
    params = req.model_dump()
    params.update(default)

    response = requests.get(SERPAPI_URL, params=params)
    if response.status_code != 200:
        return f"failed to call serpapi. error: {response.text}"

    results = response.json()
    return results["organic_results"]


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = YahooSearchRequest.model_validate(req)
    response = yahoo_search(req_typed)

    print(response)


if __name__ == '__main__':
    main()
