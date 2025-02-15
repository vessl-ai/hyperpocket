import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field


class AgentQLQueryDataRequest(BaseModel):
    query: str = Field(..., description="""AgentQL query to extract data from the webpage. The query should be enclosed in curly braces and follow these syntax rules:
    - Each term should be on a new line
    - Use lowercase with underscores (e.g., product_name)
    - Add [] after a term to get a list (e.g., products[])
    - Add descriptions in parentheses (e.g., price(integer))
    - Use nested curly braces for hierarchy

Example queries:
Single element:
{
    search_box
}

List of products with details:
{
    products[] {
        product_name
        price(integer)
        rating
    }
}

With hierarchy:
{
    header {
        sign_in_btn
    }
    footer {
        about_btn
    }
}""")
    url: str = Field(..., description="The URL of the webpage to query")
    wait_for: Optional[int] = Field(0, description="Wait time in seconds for page load (max 10 seconds)")
    is_scroll_to_bottom_enabled: Optional[bool] = Field(False,
                                                        description="Enable/disable scrolling to bottom before snapshot")
    mode: Optional[str] = Field("fast",
                                description="Extraction mode: 'standard' for complex data, 'fast' for typical use")
    is_screenshot_enabled: Optional[bool] = Field(False, description="Enable/disable screenshot capture")


def query_data(req: AgentQLQueryDataRequest):
    api_key = os.environ.get("AGENTQL_TOKEN")
    if not api_key:
        raise ValueError("AGENTQL_TOKEN environment variable is required")

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    params = {
        "wait_for": req.wait_for,
        "is_scroll_to_bottom_enabled": req.is_scroll_to_bottom_enabled,
        "mode": req.mode,
        "is_screenshot_enabled": req.is_screenshot_enabled
    }

    data = {
        "query": req.query,
        "url": req.url,
        "params": params
    }

    response = requests.post(
        "https://api.agentql.com/v1/query-data",
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        raise Exception(f"Failed to query data: {response.text}")

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = AgentQLQueryDataRequest.model_validate(req)
    response = query_data(req_typed)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
