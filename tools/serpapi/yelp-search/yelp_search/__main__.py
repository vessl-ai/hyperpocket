import json
import os
import sys
from typing import Optional, List

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class YelpSearchRequest(BaseModel):
    find_desc: Optional[str] = Field(None,
                                     description="Search query for Yelp. Can include anything used in a regular Yelp search.")
    find_loc: str = Field(...,
                          description="Location from where the search should originate. Accepts city, zip code, or address.")

    l: Optional[str] = Field(None,
                             description="Defines search radius or neighborhoods. Distance and neighborhoods can't be used together.")

    yelp_domain: Optional[str] = Field(None, description="Yelp domain to use (default: 'yelp.com').")

    cflt: Optional[str] = Field(None, description="Category filter to refine search alongside find_desc parameter.")
    sortby: Optional[str] = Field("recommended",
                                  description="Sorting option ('recommended', 'rating', 'review_count'). Default: 'recommended'.")
    attrs: Optional[List[str]] = Field(None,
                                       description="Refining filters such as 'price' or 'features'. Multiple values allowed.")

    start: Optional[int] = Field(0,
                                 description="Result offset for pagination (default: 0). Skips given number of results.")

    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format ('json' or 'html').")


def yelp_search(req: YelpSearchRequest):
    default = {
        "engine": "yelp",
        "api_key": token
    }
    params = req.model_dump()
    params.update(default)

    response = requests.get(SERPAPI_URL, params=params)
    if response.status_code != 200:
        return f"failed to call serpapi. error: {response.text}"

    results = response.json()
    if not "organic_results" in results:
        return "not found result"
    return results["organic_results"]


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = YelpSearchRequest.model_validate(req)
    response = yelp_search(req_typed)

    print(response)


if __name__ == '__main__':
    main()
