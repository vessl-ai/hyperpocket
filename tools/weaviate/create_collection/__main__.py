import json
import os
import sys

from pydantic import BaseModel, Field
import weaviate
from weaviate.classes.init import Auth


class CreateCollectionRequest(BaseModel):
    name: str = Field(..., description="The name of the collection to create.")


def create_collection(req: CreateCollectionRequest):
    WCD_URL = os.getenv('WCD_URL')
    WCD_API_KEY = os.getenv("WCD_API_KEY")

    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WCD_URL,
        auth_credentials=Auth.api_key(WCD_API_KEY),
    )

    result = client.collections.create(req.name)
    client.close()
    return result


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = CreateCollectionRequest.model_validate(req)
    print(create_collection(req_typed))


if __name__ == '__main__':
    main()
