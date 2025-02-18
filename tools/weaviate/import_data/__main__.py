import json
import os
import sys

from pydantic import BaseModel, Field
import weaviate
from weaviate.classes.init import Auth


class ImportDataRequest(BaseModel):
    collection_name: str = Field(..., description="The name of the collection to import data into.")
    data_row: str = Field(..., description="A JSON-serialized data dictionary to import into the collection.")


def import_data(req: ImportDataRequest):
    WCD_URL = os.getenv('WCD_URL')
    WEAVIATE_TOKEN = os.getenv("WEAVIATE_TOKEN")
    openai_api_key = os.environ["OPENAI_API_KEY"]

    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WCD_URL,
        auth_credentials=Auth.api_key(WEAVIATE_TOKEN),
        headers={"X-OpenAI-Api-Key": openai_api_key}
    )

    collection = client.collections.get(req.collection_name)
    with collection.batch.dynamic() as batch:
        batch.add_object(properties=json.loads(req.data_row))

        if batch.number_errors > 10:
            client.close()
            return "Batch import stopped due to excessive errors."

    failed_objects = collection.batch.failed_objects
    client.close()
    if failed_objects:
        return f"Number of failed imports: {len(failed_objects)}\nFirst failed object: {failed_objects[0]}"
    return "success"


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = ImportDataRequest.model_validate(req)
    print(import_data(req_typed))


if __name__ == '__main__':
    main()
