import json
import os
import sys
from typing import Optional, List

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class EbaySearchRequest(BaseModel):
    nkw: Optional[str] = Field(None, alias="_nkw",
                               description="Search query term for Ebay. Required unless category_id is provided.")
    category_id: Optional[int] = Field(None,
                                       description="Category ID for concentrated search. Can be used without nkw.")

    ebay_domain: Optional[str] = Field("ebay.com", description="Ebay domain to use (default: ebay.com)")
    salic: Optional[str] = Field(None, alias="_salic", description="Location based on country.")

    pgn: Optional[int] = Field(1, alias="_pgn", ge=1, description="Page number for pagination (default: 1)")
    ipg: Optional[int] = Field(50, alias="_ipg",
                               description="Max results per page. Options: 25, 50 (default), 100, 200")

    blrs: Optional[str] = Field(None, alias="_blrs",
                                description="Exclude results from auto-corrected queries if spell_auto_correct is used.")
    show_only: Optional[List[str]] = Field(None, description="List of filters to apply to results (e.g., 'Sold', 'FS')")
    buying_format: Optional[List[str]] = Field(None, description="Buying format filter (e.g., 'Auction', 'BIN', 'BO')")

    udlo: Optional[float] = Field(None, alias="_udlo", description="Lowest price filter.")
    udhi: Optional[float] = Field(None, alias="_udhi", description="Highest price filter.")
    sop: Optional[int] = Field(12, alias="_sop", description="Sorting method for results. (default: 12(best match))")
    dmd: Optional[str] = Field(None, alias="_dmd", description="Visual layout (Grid or List)")

    stpos: Optional[str] = Field(None, alias="_stpos",
                                 description="ZIP or Postal code for filtering shipping products by area.")
    LH_ItemCondition: Optional[str] = Field(None,
                                            description="Product condition filter using numeric IDs (e.g., '1000|3000').")

    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format: 'json' (default) or 'html'")

    class Config:
        populate_by_name = True


def ebay_search(req: EbaySearchRequest):
    default = {
        "engine": "ebay",
        "api_key": token
    }
    params = req.model_dump(by_alias=True)
    params.update(default)

    response = requests.get(SERPAPI_URL, params=params)
    if response.status_code != 200:
        return f"failed to call serpapi. error: {response.text}"

    results = response.json()
    organic_results = results["organic_results"]
    return organic_results


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = EbaySearchRequest.model_validate(req)
    response = ebay_search(req_typed)

    print(response)


if __name__ == '__main__':
    main()
