import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class GoogleShoppingRequest(BaseModel):
    q: str = Field(..., description="Search query for Google Shopping.")

    location: Optional[str] = Field(None, description="Location to originate the search from.")
    uule: Optional[str] = Field(None, description="Google encoded location for search. Can't be used with location.")

    google_domain: Optional[str] = Field("google.com", description="Google domain to use (default: 'google.com').")
    gl: Optional[str] = Field("us", description="Country code for search localization (default: 'us').")
    hl: Optional[str] = Field("en", description="Language code for search localization (default: 'en').")

    tbs: Optional[str] = Field(None, description="Advanced search filters for specific content types.")
    shoprs: Optional[str] = Field(None, description="Helper ID for setting search filters.")
    direct_link: Optional[bool] = Field(False, description="Include direct link of each product (default: False).")

    start: Optional[int] = Field(0,
                                 description="Pagination offset for results (default: 0). Not recommended for the new layout.")
    num: Optional[int] = Field(60, ge=1, le=100,
                               description="Number of results to return (default: 60, max: 100). Not supported in new layout.")

    device: Optional[str] = Field("desktop", description="Device type ('desktop', 'tablet', 'mobile').")
    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format ('json' or 'html').")


def google_shopping(req: GoogleShoppingRequest):
    default = {
        "engine": "google_shopping",
        "api_key": token
    }
    params = req.model_dump()
    params.update(default)

    response = requests.get(SERPAPI_URL, params=params)
    if response.status_code != 200:
        return f"failed to call serpapi. error: {response.text}"

    results = response.json()
    return results["shopping_results"]


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleShoppingRequest.model_validate(req)
    response = google_shopping(req_typed)

    print(response)


if __name__ == '__main__':
    main()
