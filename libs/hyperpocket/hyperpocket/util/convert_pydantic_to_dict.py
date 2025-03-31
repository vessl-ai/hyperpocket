from typing import Any

from pydantic import BaseModel


def convert_pydantic_to_dict(data: Any):
    if isinstance(data, BaseModel):
        return data.model_dump()
    elif isinstance(data, dict):
        return {key: convert_pydantic_to_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_pydantic_to_dict(item) for item in data]

    return data