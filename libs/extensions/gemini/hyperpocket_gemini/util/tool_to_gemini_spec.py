from google.genai import types

from hyperpocket.tool import Tool
from hyperpocket.util.flatten_json_schema import flatten_json_schema


def tool_to_gemini_spec(tool: Tool, use_profile: bool) -> types.Tool:
    arg_schema = tool.schema_model(use_profile=use_profile)
    json_schema = arg_schema.model_json_schema()
    json_schema = flatten_json_schema(json_schema)

    function = types.FunctionDeclaration(
        name=json_schema.get("title"),
        description=json_schema.get("description", ""),
        parameters=_convert_json_schema_to_gemini_spec(json_schema)
    )

    gemini_tool = types.Tool(function_declarations=[function])

    return gemini_tool


def _convert_json_schema_to_gemini_spec(schema: dict):
    properties = schema.get('properties', {})
    if len(properties) == 0:
        return None

    schemas = {}
    for key, value in properties.items():
        type = value.get("type")
        if type == "OBJECT":
            schema[key] = _convert_json_schema_to_gemini_spec(value)
        else:
            schemas[key] = types.Schema(
                type=str(value.get('type')).upper(),
            )
    return types.Schema(
        type="OBJECT",
        description=schema.get('description', ''),
        required=schema.get('required', []),
        properties=schemas,
    )
