import json
import os
import sys

from pydantic import BaseModel, Field
import weaviate
from weaviate.classes.init import Auth


class QueryNearTextRequest(BaseModel):
    collection_name: str = Field(..., description="The name of the collection to read objects from.")
    query: str = Field(..., description="The user prompt query")
    limit: int = Field(3, description="The number of results to return")


def query_near_text(req: QueryNearTextRequest):
    WCD_URL = os.getenv('WCD_URL')
    WCD_API_KEY = os.getenv("WEAVIATE_TOKEN")
    openai_api_key = os.environ["OPENAI_API_KEY"]

    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WCD_URL,
        auth_credentials=Auth.api_key(WCD_API_KEY),
        headers={"X-OpenAI-Api-Key": openai_api_key}
    )

    collection = client.collections.get(req.collection_name)
    
    response = collection.query.near_text(
        query=req.query,
        limit=req.limit,
    )
    
    client.close()

    return response


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = QueryNearTextRequest.model_validate(req)
    resp = query_near_text(req_typed)
    resp_serialized = [obj.properties for obj in resp.objects]
    print(json.dumps(resp_serialized, indent=2))


if __name__ == '__main__':
    main()
