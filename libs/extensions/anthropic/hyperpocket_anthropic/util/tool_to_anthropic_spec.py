from hyperpocket.tool import Tool
from hyperpocket.util.flatten_json_schema import flatten_json_schema


def tool_to_anthropic_spec(tool: Tool, use_profile: bool) -> dict:
    name = tool.name
    description = tool.get_description(use_profile=use_profile)
    arg_schema = tool.schema_model(use_profile=use_profile)
    json_schema = flatten_json_schema(arg_schema.model_json_schema())

    anthropic_spec = {
        "name": name,
        "description": description.strip(),
        "input_schema": {
            "type": json_schema["type"],
            "properties": json_schema["properties"],
            "required": json_schema.get("required", []),
            "title": json_schema.get("title", ""),
        },
    }

    return anthropic_spec
