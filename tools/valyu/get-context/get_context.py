import json
import os
import sys
from pydantic import BaseModel
from valyu import Valyu

# Setup Valyu client
valyu = Valyu(api_key=os.getenv("VALYU_API_KEY"))

class ValyuGetContextRequest(BaseModel):
    query: str
    search_type: str = "all"
    max_num_results: int = 10
    max_price: int = 10

def get_context(req: ValyuGetContextRequest):
    response = valyu.context(**req.model_dump())
    return response

def main():
    req = json.load(sys.stdin.buffer)
    req_typed = ValyuGetContextRequest.model_validate(req)

    response = get_context(req_typed)

    print(response)


if __name__ == '__main__':
    main()
