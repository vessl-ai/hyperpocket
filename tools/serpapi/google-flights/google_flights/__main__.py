import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class GoogleFlightsRequest(BaseModel):
    departure_id: Optional[str] = Field(None,
                                        description="Departure airport code or location kgmid. Multiple values separated by commas.")
    arrival_id: Optional[str] = Field(None,
                                      description="Arrival airport code or location kgmid. Multiple values separated by commas.")

    gl: Optional[str] = Field(None, description="Country code for Google Flights search (e.g., 'us', 'uk', 'fr').")
    hl: Optional[str] = Field(None, description="Language code for Google Flights search (e.g., 'en', 'es', 'fr').")
    currency: Optional[str] = Field("USD", description="Currency of returned prices (default: 'USD').")

    type: Optional[int] = Field(1, description="Type of flight (1: Round trip, 2: One way, 3: Multi-city). Default: 1.")
    outbound_date: Optional[str] = Field(None, description="Outbound date in YYYY-MM-DD format.")
    return_date: Optional[str] = Field(None, description="Return date in YYYY-MM-DD format. Required for Round trip.")

    travel_class: Optional[int] = Field(1,
                                        description="Travel class (1: Economy, 2: Premium economy, 3: Business, 4: First). Default: 1.")
    multi_city_json: Optional[str] = Field(None, description="JSON string containing multi-city flight information.")

    show_hidden: Optional[bool] = Field(False, description="Include hidden flight results (default: False).")
    deep_search: Optional[bool] = Field(False, description="Enable deep search for better results (default: False).")

    adults: Optional[int] = Field(1, description="Number of adults (default: 1).")
    children: Optional[int] = Field(0, description="Number of children (default: 0).")
    infants_in_seat: Optional[int] = Field(0, description="Number of infants in seat (default: 0).")
    infants_on_lap: Optional[int] = Field(0, description="Number of infants on lap (default: 0).")

    sort_by: Optional[int] = Field(1,
                                   description="Sorting order (1: Top flights, 2: Price, 3: Departure time, 4: Arrival time, 5: Duration, 6: Emissions). Default: 1.")

    stops: Optional[int] = Field(0,
                                 description="Number of stops (0: Any, 1: Nonstop, 2: 1 stop, 3: 2 stops). Default: 0.")
    exclude_airlines: Optional[str] = Field(None, description="Comma-separated list of airline codes to exclude.")
    include_airlines: Optional[str] = Field(None, description="Comma-separated list of airline codes to include.")
    bags: Optional[int] = Field(0, description="Number of carry-on bags (default: 0).")
    max_price: Optional[int] = Field(None, description="Maximum ticket price (default: unlimited).")

    outbound_times: Optional[str] = Field(None, description="Outbound times range as comma-separated values.")
    return_times: Optional[str] = Field(None, description="Return times range as comma-separated values.")

    emissions: Optional[int] = Field(None, description="Emission level filter (1: Less emissions only).")
    layover_duration: Optional[str] = Field(None, description="Layover duration range in minutes (e.g., '90,330').")
    exclude_conns: Optional[str] = Field(None, description="Comma-separated list of connecting airports to exclude.")
    max_duration: Optional[int] = Field(None, description="Maximum flight duration in minutes.")

    departure_token: Optional[str] = Field(None,
                                           description="Token for selecting departing flights for round trip/multi-city.")
    booking_token: Optional[str] = Field(None, description="Token for fetching booking options for selected flights.")

    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format: 'json' (default) or 'html'.")


def google_flights(req: GoogleFlightsRequest):
    default = {
        "engine": "google_flights",
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
    req_typed = GoogleFlightsRequest.model_validate(req)
    response = google_flights(req_typed)

    print(response)


if __name__ == '__main__':
    main()
