import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class GoogleScholarRequest(BaseModel):
    q: Optional[str] = Field(None, description="Search query for Google Scholar. Can't be used with cluster parameter.")
    cites: Optional[str] = Field(None,
                                 description="Unique ID for an article to trigger Cited By searches. Can't be used with cluster.")
    as_ylo: Optional[int] = Field(None, description="Year from which results should be included.")
    as_yhi: Optional[int] = Field(None, description="Year until which results should be included.")
    scisbd: Optional[int] = Field(0,
                                  description="Sort articles by date (1: Abstracts only, 2: Everything, 0: Sorted by relevance).")
    cluster: Optional[str] = Field(None,
                                   description="Unique ID for an article to trigger All Versions searches. Can't be used with q or cites.")

    hl: Optional[str] = Field("en", description="Language code for Google Scholar search (default: 'en').")
    lr: Optional[str] = Field(None, description="Languages to limit search to (e.g., 'lang_fr|lang_de').")

    start: Optional[int] = Field(0, description="Result offset for pagination (default: 0).")
    num: Optional[int] = Field(10, ge=1, le=20,
                               description="Maximum number of results to return (default: 10, max: 20).")

    as_sdt: Optional[str] = Field("0",
                                  description="Search type or filter (0: Exclude patents, 7: Include patents, 4: Select case law).")

    safe: Optional[str] = Field("off", description="Filtering level for adult content ('active' or 'off').")
    filter: Optional[int] = Field(1,
                                  description="Enable filters for 'Similar Results' and 'Omitted Results' (1: On, 0: Off).")
    as_vis: Optional[int] = Field(0, description="Include citations in results (1: Exclude, 0: Include).")
    as_rr: Optional[int] = Field(0, description="Show only review articles (1: Yes, 0: No).")

    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format: 'json' (default) or 'html'.")


def google_scholar(req: GoogleScholarRequest):
    default = {
        "engine": "google_scholar",
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
    req_typed = GoogleScholarRequest.model_validate(req)
    response = google_scholar(req_typed)

    print(response)


if __name__ == '__main__':
    main()
