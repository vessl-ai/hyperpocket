import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class GoogleNewsRequest(BaseModel):
    q: Optional[str] = Field(None,
                             description="Search query for Google News. Can't be used with publication_token, story_token, or topic_token.")

    gl: Optional[str] = Field("us", description="Country code for Google News search (default: 'us').")
    hl: Optional[str] = Field("en", description="Language code for Google News search (default: 'en').")

    topic_token: Optional[str] = Field(None,
                                       description="Google News topic token. Can't be used with q, story_token, or publication_token.")
    publication_token: Optional[str] = Field(None,
                                             description="Google News publication token. Can't be used with q, story_token, or topic_token.")
    section_token: Optional[str] = Field(None,
                                         description="Google News section token. Can only be used with topic_token or publication_token.")
    story_token: Optional[str] = Field(None,
                                       description="Google News story token for full coverage. Can't be used with q, topic_token, or publication_token.")

    so: Optional[int] = Field(0,
                              description="Sorting order (0: Relevance, 1: Date). Can only be used with story_token.")

    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format: 'json' (default) or 'html'.")


def google_news(req: GoogleNewsRequest):
    default = {
        "engine": "google_news",
        "api_key": token
    }
    params = req.model_dump()
    params.update(default)

    response = requests.get(SERPAPI_URL, params=params)
    if response.status_code != 200:
        return f"failed to call serpapi. error: {response.text}"

    results = response.json()
    return results["news_results"]


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GoogleNewsRequest.model_validate(req)
    response = google_news(req_typed)

    print(response)


if __name__ == '__main__':
    main()
