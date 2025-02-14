import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class YoutubeSearchRequest(BaseModel):
    search_query: str = Field(..., description="Search query for YouTube.")

    gl: Optional[str] = Field(None, description="Country code for search localization (e.g., 'us', 'uk', 'fr').")
    hl: Optional[str] = Field(None, description="Language code for search localization (e.g., 'en', 'es', 'fr').")

    sp: Optional[str] = Field(None,
                              description="Parameter for pagination or filtering search results. Accepts encoded filter values.")

    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format ('json' or 'html').")


def youtube_search(req: YoutubeSearchRequest):
    default = {
        "engine": "youtube",
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
    req_typed = YoutubeSearchRequest.model_validate(req)
    response = youtube_search(req_typed)

    print(response)


if __name__ == '__main__':
    main()
