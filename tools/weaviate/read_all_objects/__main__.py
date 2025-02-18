import json
import os
import sys

from pydantic import BaseModel, Field
import weaviate
from weaviate.classes.init import Auth


class ReadAllObjectsRequest(BaseModel):
    collection_name: str = Field(..., description="The name of the collection to read objects from.")
    include_vector: bool = Field(True, description="Whether to include vectors in the response.")


def read_all_objects(req: ReadAllObjectsRequest):
    WCD_URL = os.getenv('WCD_URL')
    WCD_API_KEY = os.getenv("WCD_API_KEY")

    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WCD_URL,
        auth_credentials=Auth.api_key(WCD_API_KEY),
    )

    collection = client.collections.get(req.collection_name)
    results = []
    for item in collection.iterator(include_vector=req.include_vector):
        results.append({
            "properties": item.properties,
            "vector": item.vector
        })

    client.close()
    return results


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = ReadAllObjectsRequest.model_validate(req)
    print(json.dumps(read_all_objects(req_typed), indent=2))


if __name__ == '__main__':
    main()
