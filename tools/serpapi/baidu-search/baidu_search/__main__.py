import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class BaiduSearchRequest(BaseModel):
    q: str = Field(..., description="Search query including all Baidu search operators")

    ct: Optional[int] = Field(1,
                              description="Language restriction (1: All, 2: Simplified Chinese, 3: Traditional Chinese)")

    pn: Optional[int] = Field(0, ge=0,
                              description="Result offset for pagination (e.g., 0 for first page, 10 for second page)")
    rn: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of results to return (default: 10, max: 50)")

    gpc: Optional[str] = Field("", description="Time period filter using Unix Timestamp")
    q5: Optional[int] = Field(None, description="Search filter (1: by title, 2: by URL)")
    q6: Optional[str] = Field("", description="Domain restriction for search results")

    bs: Optional[str] = Field("", description="Previous search query")
    oq: Optional[str] = Field("", description="Original search query when navigated from a related search")
    f: Optional[int] = Field(None,
                             description="Originating search type (8: normal, 3: suggestion list, 1: related search)")

    device: Optional[str] = Field("desktop", description="Device type ('desktop', 'tablet', or 'mobile')")
    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode")

    output: Optional[str] = Field("json", description="Output format: 'json' (default) or 'html'")


def baidu_search(req: BaiduSearchRequest):
    default = {
        "engine": "baidu",
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
    req_typed = BaiduSearchRequest.model_validate(req)
    response = baidu_search(req_typed)

    print(response)


if __name__ == '__main__':
    main()
