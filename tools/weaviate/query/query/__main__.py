import json
import os
import sys

from pydantic import BaseModel, Field
import weaviate

token = os.getenv('WEAVIATE_TOKEN')


class QueryRequest(BaseModel):
    test: str = Field(description="")


def query(req: QueryRequest):
    pass


def main():
    print("Weaviate version: ", weaviate.__version__)


if __name__ == '__main__':
    main()