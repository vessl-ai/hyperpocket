import json
import os
import sys
import requests

from pydantic import BaseModel, Field

token = os.getenv('SEMANTIC_SCHOLAR_TOKEN')


class GetGraphGetPaperRequest(BaseModel):
    paper_id: int = Field(description="Semantic Scholar ID")


def get_graph_paper(req: GetGraphGetPaperRequest):
    response = requests.get(
        url="https://api.semanticscholar.org/graph/v1/paper",
        headers={
            "Authorization": f"Bearer {token}",
        },
        params = req.model_dump(),
    )
    
    if response.status_code != 200:
        return f"failed to insert semantic scholar events. error : {response.text}"

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GetGraphGetPaperRequest.model_validate(req)
    response = get_graph_paper(req_typed)

    print(response)


if __name__ == '__main__':
    main()