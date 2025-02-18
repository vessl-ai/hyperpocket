import json
import os
import sys

from pydantic import BaseModel, Field
import weaviate
from weaviate.classes.init import Auth


class ReadObjectByIdRequest(BaseModel):
    collection_name: str = Field(..., description="The name of the collection to read the object from.")
    object_id: str = Field(..., description="The ID of the object to read.")


def read_object_by_id(req: ReadObjectByIdRequest):
    WCD_URL = os.getenv('WCD_URL')
    WEAVIATE_TOKEN = os.getenv("WEAVIATE_TOKEN")

    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WCD_URL,
        auth_credentials=Auth.api_key(WEAVIATE_TOKEN),
    )

    collection = client.collections.get(req.collection_name)
    data_object = collection.query.fetch_object_by_id(req.object_id)
    result = {
        "id": str(data_object.uuid),
        "properties": data_object.properties,
        "vector": data_object.vector
    }
    client.close()
    return result


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = ReadObjectByIdRequest.model_validate(req)
    print(json.dumps(read_object_by_id(req_typed), indent=2))


if __name__ == '__main__':
    main()
