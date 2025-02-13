import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class WalmartSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query for Walmart. Either query or cat_id is required.")

    sort: Optional[str] = Field(None,
                                description="Sorting option (e.g., 'price_low', 'price_high', 'best_seller', 'best_match', 'rating_high', 'new').")
    soft_sort: Optional[bool] = Field(True,
                                      description="Enable sort by relevance (default: True). Set to False to disable relevance sorting.")

    cat_id: Optional[str] = Field(None,
                                  description="Category ID for Walmart search. Either query or cat_id is required.")
    facet: Optional[str] = Field(None,
                                 description="Filter items based on attributes using 'key:value' pairs separated by '||'.")
    store_id: Optional[str] = Field(None, description="Filter products by specific Walmart store ID.")

    min_price: Optional[float] = Field(None, description="Lower bound of price range.")
    max_price: Optional[float] = Field(None, description="Upper bound of price range.")
    spelling: Optional[bool] = Field(True, description="Enable spelling fix (default: True). Set to False to disable.")
    nd_en: Optional[bool] = Field(False, description="Show results with NextDay delivery only (default: False).")

    page: Optional[int] = Field(1, ge=1, le=100, description="Page number for pagination (default: 1, max: 100).")

    device: Optional[str] = Field("desktop", description="Device type ('desktop', 'tablet', 'mobile').")
    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")
    include_filters: Optional[bool] = Field(False, description="Include filters in JSON response (default: False).")

    output: Optional[str] = Field("json", description="Output format ('json' or 'html').")


def walmart_search(req: WalmartSearchRequest):
    default = {
        "engine": "walmart",
        "api_key": token
    }
    params = req.model_dump()
    params.update(default)

    response = requests.get(SERPAPI_URL, params=params)
    if response.status_code != 200:
        return f"failed to call serpapi. error: {response.text}"

    results = response.json()
    if "error" in results:
        return results["error"]

    return results["organic_results"]


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = WalmartSearchRequest.model_validate(req)
    response = walmart_search(req_typed)

    print(response)


if __name__ == '__main__':
    main()
