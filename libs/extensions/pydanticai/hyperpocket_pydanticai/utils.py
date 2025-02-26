from inspect import Parameter, Signature
from typing import Any


def _map_json_type_to_python(json_type: str) -> Any:
    """Map JSON schema type to Python type."""
    type_mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    return type_mapping.get(json_type, Any)


def _process_schema_properties(json_schema: dict) -> list[tuple[str, dict, bool]]:
    """Process JSON schema properties into a standardized format.

    Args:
        json_schema (dict): The JSON schema describing the function parameters.

    Returns:
        list[tuple[str, dict, bool]]: List of tuples containing
            (param_name, param_info, is_required).
    """
    properties = json_schema.get("properties", {})
    required_params = json_schema.get("required", [])

    return [(name, info, name in required_params) for name, info in properties.items()]


def generate_docstring(description: str, json_schema: dict) -> str:
    """Generate a Google-style docstring from a description and JSON schema.

    Args:
        description (str): The description of the function.
        json_schema (dict): The JSON schema describing the function parameters.

    Returns:
        str: A docstring.
    """
    docstring = f"{description}\n\n"

    properties = json_schema.get("properties")
    if properties is not None:
        docstring += "Args:\n"
        for param_name, param_info in properties.items():
            param_type = param_info.get("type", "Any")
            param_desc = param_info.get("description", "")
            required = param_name in json_schema.get("required", [])
            req_note = " (Required)" if required else ""
            docstring += f"    {param_name} ({param_type}){req_note}: {param_desc}\n"

    docstring += "\nReturns:\n    str | None: The result of the tool execution as a string, or None if no result."

    return docstring


def generate_annotations(json_schema: dict) -> dict[str, Any]:
    """Generate a type annotations dictionary from a JSON schema.

    Args:
        json_schema (dict): The JSON schema describing the function parameters.

    Returns:
        dict[str, Any]: A dictionary mapping parameter names to their type annotations.
    """
    annotations = {}

    # If no properties, return just the return empty annotation
    if not json_schema.get("properties"):
        return annotations

    # Map properties to type annotations
    for param_name, param_info in json_schema.get("properties", {}).items():
        json_type = param_info.get("type", "string")
        annotations[param_name] = _map_json_type_to_python(json_type)

    return annotations


def create_signature(json_schema: dict, return_type: Any = str | None) -> Signature:
    """Create a function signature from a JSON schema."""
    if not json_schema.get("properties"):
        # If no properties, return a simple signature with just **kwargs
        kwargs_param = Parameter("kwargs", Parameter.VAR_KEYWORD)
        return Signature([kwargs_param], return_annotation=return_type)

    # Create parameters from the properties
    parameters = []
    processed_props = _process_schema_properties(json_schema)

    for param_name, param_info, required in processed_props:
        # Determine default value and kind
        kind = Parameter.POSITIONAL_OR_KEYWORD
        default = Parameter.empty if required else None

        # Get type annotation
        json_type = param_info.get("type", "string")
        annotation = _map_json_type_to_python(json_type)

        # Create parameter
        param = Parameter(param_name, kind, default=default, annotation=annotation)
        parameters.append(param)

    # Add a kwargs parameter to handle any additional arguments if additionalProperties is true
    if json_schema.get("additionalProperties", False):
        kwargs_param = Parameter("kwargs", Parameter.VAR_KEYWORD)
        parameters.append(kwargs_param)

    # Create a new signature
    return Signature(parameters, return_annotation=return_type)
