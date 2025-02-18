import json
import os
import sys

from pydantic import BaseModel, Field
import weaviate
from weaviate.classes.init import Auth
import weaviate.classes.config as wc


class CreateCollectionRequest(BaseModel):
    name: str = Field(..., description="The name of the collection to create.")


def create_collection(req: CreateCollectionRequest):
    WCD_URL = os.getenv('WCD_URL')
    WEAVIATE_TOKEN = os.getenv("WEAVIATE_TOKEN")

    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WCD_URL,
        auth_credentials=Auth.api_key(WEAVIATE_TOKEN),
    )

    client.collections.create(
        req.name,
        vectorizer_config=wc.Configure.Vectorizer.text2vec_openai(),
    )
    client.close()
    print(f"Collection {req.name} created successfully.")


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = CreateCollectionRequest.model_validate(req)
    create_collection(req_typed)


if __name__ == '__main__':
    main()
