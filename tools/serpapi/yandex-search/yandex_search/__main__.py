import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field

token = os.getenv('SERPAPI_TOKEN')
SERPAPI_URL = "https://serpapi.com/search.json"


class YandexSearchRequest(BaseModel):
    text: str = Field(..., description="Search query for Yandex.")

    yandex_domain: Optional[str] = Field("yandex.com", description="Yandex domain to use (default: 'yandex.com').")
    lang: Optional[str] = Field("en",
                                description="Language for Yandex search (default: 'en' for yandex.com). Use comma-separated values for multiple languages.")

    lr: Optional[int] = Field(None,
                              description="Country or region ID to limit search results. Defaults to matching location of selected yandex_domain.")
    rstr: Optional[bool] = Field(None,
                                 description="Enable additional filtering to include specified location in text snippets/titles.")

    p: Optional[int] = Field(0, description="Page number for pagination (default: 0).")

    no_cache: Optional[bool] = Field(False, description="Force fetching new results instead of cached results.")
    async_search: Optional[bool] = Field(False, alias="async", description="Submit search asynchronously.")
    zero_trace: Optional[bool] = Field(False, description="Enterprise-only: Enable ZeroTrace mode.")

    output: Optional[str] = Field("json", description="Output format ('json' or 'html').")


def yandex_search(req: YandexSearchRequest):
    default = {
        "engine": "yandex",
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
    req_typed = YandexSearchRequest.model_validate(req)
    response = yandex_search(req_typed)

    print(response)


if __name__ == '__main__':
    main()
