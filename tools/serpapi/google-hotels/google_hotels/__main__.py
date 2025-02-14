import json
import os
import sys
from typing import Optional, List

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class GoogleHotelsRequest(BaseModel):
    q: str = Field(..., description="Search query for Google Hotels.")

    gl: Optional[str] = Field(None, description="Country code for Google Hotels search (e.g., 'us', 'uk', 'fr').")
    hl: Optional[str] = Field(None, description="Language code for Google Hotels search (e.g., 'en', 'es', 'fr').")
    currency: Optional[str] = Field("USD", description="Currency of returned prices (default: 'USD').")

    check_in_date: str = Field(..., description="Check-in date in YYYY-MM-DD format.")
    check_out_date: str = Field(..., description="Check-out date in YYYY-MM-DD format.")

    adults: Optional[int] = Field(2, description="Number of adults (default: 2).")
    children: Optional[int] = Field(0, description="Number of children (default: 0).")
    children_ages: Optional[List[int]] = Field(None, description="Ages of children, from 1 to 17 years old.")

    sort_by: Optional[int] = Field(None,
                                   description="Sorting order (3: Lowest price, 8: Highest rating, 13: Most reviewed).")
    min_price: Optional[int] = Field(None, description="Lower bound of price range.")
    max_price: Optional[int] = Field(None, description="Upper bound of price range.")

    property_types: Optional[List[int]] = Field(None, description="Filter by property type (e.g., '17,12,18').")
    amenities: Optional[List[int]] = Field(None, description="Filter by amenities (e.g., '35,9,19').")
    rating: Optional[int] = Field(None, description="Filter by rating (7: 3.5+, 8: 4.0+, 9: 4.5+).")

    brands: Optional[List[int]] = Field(None,
                                        description="Filter by hotel brands (not available for Vacation Rentals).")
    hotel_class: Optional[List[int]] = Field(None, description="Filter by hotel class (2: 2-star, 3: 3-star, etc.).")
    free_cancellation: Optional[bool] = Field(None, description="Show results with free cancellation.")
    special_offers: Optional[bool] = Field(None, description="Show results with special offers.")
    eco_certified: Optional[bool] = Field(None, description="Show results that are eco-certified.")

    vacation_rentals: Optional[bool] = Field(False, description="Search for vacation rentals instead of hotels.")
    bedrooms: Optional[int] = Field(0, description="Minimum number of bedrooms (only for Vacation Rentals).")
    bathrooms: Optional[int] = Field(0, description="Minimum number of bathrooms (only for Vacation Rentals).")

    next_page_token: Optional[str] = Field(None, description="Token for retrieving the next page of results.")
    property_token: Optional[str] = Field(None, description="Token for retrieving property details.")

    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format: 'json' (default) or 'html'.")


def google_hotels(req: GoogleHotelsRequest):
    default = {
        "engine": "google_hotels",
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
    req_typed = GoogleHotelsRequest.model_validate(req)
    response = google_hotels(req_typed)

    print(response)


if __name__ == '__main__':
    main()
