import json
import os
import sys
from typing import Optional

import requests
from pydantic import BaseModel, Field


class ActiveloopQueryRequest(BaseModel):
    dataset_path: str = Field(..., description="The path to the Deep Lake dataset (e.g. hub://org_id/dataset_name). This same path must be used in the FROM clause of your query.")
    query: str = Field(..., description="""SQL-like query to search the dataset. The query must include FROM clause with the exact dataset_path. The query should follow these rules:
    - Use 'select' to specify fields to return
    - Use 'from' with the dataset_path
    - Use 'where' for filtering (optional)
    - Use 'order by' for sorting (optional)
    - Use 'limit' to restrict results (optional)

Example queries:
Basic select:
select * from "hub://org/dataset"

Vector similarity search:
select text, cosine_similarity(embedding, ARRAY[0.1,0.2,...]) as score 
from "hub://org/dataset" 
order by score desc 
limit 5""")
    as_list: Optional[bool] = Field(True, description="If True, returns results as a list of objects. If False, returns results grouped by tensor")


def query_data(req: ActiveloopQueryRequest):
    token = os.environ.get("ACTIVELOOP_TOKEN")
    if not token:
        raise ValueError("ACTIVELOOP_TOKEN environment variable is required")

    # Validate that the query includes the correct dataset path
    if f'"{req.dataset_path}"' not in req.query:
        raise ValueError(f"Query must include FROM clause with the exact dataset path: {req.dataset_path}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "query": req.query,
        "as_list": req.as_list
    }

    response = requests.post(
        "https://app.activeloop.ai/api/query/v1",
        headers=headers,
        json=data
    )

    if response.status_code != 200:
        raise Exception(f"Failed to query data: {response.text}")

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = ActiveloopQueryRequest.model_validate(req)
    response = query_data(req_typed)

    print(json.dumps(response))


if __name__ == "__main__":
    main() 