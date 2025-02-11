import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class NaverSearchRequest(BaseModel):
    query: str = Field(..., description="Search query for Naver. Supports advanced search operators.")

    start: Optional[int] = Field(1, description="Offset for organic results. Defaults to 1.")
    page: Optional[int] = Field(None,
                                description="Page number for pagination. Automatically calculates start parameter.")
    num: Optional[int] = Field(50, ge=1, le=100,
                               description="Maximum number of results to return (default: 50, max: 100). Only applicable for Naver Images API.")

    where: Optional[str] = Field("nexearch",
                                 description="Search type (e.g., 'nexearch', 'web', 'video', 'news', 'image').")

    device: Optional[str] = Field("desktop", description="Device type ('desktop', 'tablet', 'mobile').")
    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format ('json' or 'html').")


def naver_search(req: NaverSearchRequest):
    default = {
        "engine": "naver",
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
    req_typed = NaverSearchRequest.model_validate(req)
    response = naver_search(req_typed)

    print(response)


if __name__ == '__main__':
    main()
