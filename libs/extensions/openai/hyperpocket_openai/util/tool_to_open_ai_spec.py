from hyperpocket.tool import Tool
from hyperpocket.util.flatten_json_schema import flatten_json_schema


def tool_to_open_ai_spec(tool: Tool, use_profile: bool) -> dict:
    name = tool.name
    description = tool.get_description(use_profile=use_profile)
    arg_schema = tool.schema_model(use_profile=use_profile)
    json_schema = arg_schema.model_json_schema()
    json_schema = flatten_json_schema(json_schema)

    openai_spec = {
        "type": "function",
        "function": {
            "name": name,
            "description": description.strip(),
            "parameters": {**json_schema},
        },
    }

    return openai_spec
