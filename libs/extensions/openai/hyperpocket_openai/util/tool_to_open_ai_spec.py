from hyperpocket.util.flatten_json_schema import flatten_json_schema
from hyperpocket.tool import Tool


def tool_to_open_ai_spec(tool: Tool) -> dict:
    name = tool.name
    description = tool.description
    arg_schema = tool.schema_model()
    json_schema = arg_schema.model_json_schema()
    json_schema = flatten_json_schema(json_schema)

    openai_spec = {
        "type": "function",
        "function": {
            "name": name,
            "description": description.strip(),
            "parameters": {
                **json_schema
            },
        }
    }

    return openai_spec
