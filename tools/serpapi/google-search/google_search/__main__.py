import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class GoogleSearchRequest(BaseModel):
    q: str = Field(..., description="Search query for Google. Supports advanced search operators.")

    location: Optional[str] = Field(None, description="Location to originate the search from.")
    uule: Optional[str] = Field(None, description="Google encoded location for search. Can't be used with location.")

    ludocid: Optional[str] = Field(None, description="Google My Business listing ID (CID) to scrape.")
    lsig: Optional[str] = Field(None, description="Forces knowledge graph map view to show up.")
    kgmid: Optional[str] = Field(None, description="Google Knowledge Graph ID to scrape.")
    si: Optional[str] = Field(None, description="Cached search parameters for Google Search.")
    ibp: Optional[str] = Field(None, description="Controls rendering and expansions for specific elements.")
    uds: Optional[str] = Field(None, description="Filter search results using a Google-provided filter string.")

    google_domain: Optional[str] = Field("google.com", description="Google domain to use (default: 'google.com').")
    gl: Optional[str] = Field("us", description="Country code for search localization (default: 'us').")
    hl: Optional[str] = Field("en", description="Language code for search localization (default: 'en').")
    cr: Optional[str] = Field(None, description="Country restriction for search (e.g., 'countryFR|countryDE').")
    lr: Optional[str] = Field(None, description="Language restriction for search (e.g., 'lang_fr|lang_de').")

    tbs: Optional[str] = Field(None, description="Advanced search filters for specific content types.")
    safe: Optional[str] = Field("off", description="Filtering level for adult content ('active' or 'off').")
    nfpr: Optional[int] = Field(0, description="Exclude results from auto-corrected query (1: Yes, 0: No).")
    filter: Optional[int] = Field(1,
                                  description="Enable 'Similar Results' and 'Omitted Results' filters (1: On, 0: Off).")

    tbm: Optional[str] = Field(None, description="Type of Google search (e.g., 'isch' for images, 'vid' for videos).")

    start: Optional[int] = Field(0,
                                 description="Pagination offset for results (default: 0). Google Local Results only accept multiples of 20.")
    num: Optional[int] = Field(10, ge=1, le=100, description="Number of results to return (default: 10, max: 100).")

    device: Optional[str] = Field("desktop", description="Device type ('desktop', 'tablet', 'mobile').")
    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format ('json' or 'html').")


def google_search(req: GoogleSearchRequest):
    default = {
        "engine": "google",
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
    req_typed = GoogleSearchRequest.model_validate(req)
    response = google_search(req_typed)

    print(response)


if __name__ == '__main__':
    main()
