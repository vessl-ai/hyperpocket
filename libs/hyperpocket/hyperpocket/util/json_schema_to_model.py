from typing import Type

from pydantic import BaseModel, create_model, Field


# Convert JSON Schema to a Pydantic model
def json_schema_to_model(schema: dict, model_name: str = "DynamicModel") -> Type[BaseModel]:
    """Recursively create a Pydantic model from a JSON Schema."""
    fields = {}
    config_extra = "forbid"

    required_fields = schema.get("required", [])
    for property_name, property_schema in schema.get("properties", {}).items():
        field_type, field_default, field_description, required = None, None, None, False
        if "type" in property_schema:
            json_type = property_schema["type"]
            if json_type == "integer":
                field_type = int
            elif json_type == "string":
                field_type = str
            elif json_type == "object":
                if "properties" in property_schema:
                    # Recursively create nested models
                    field_type = json_schema_to_model(property_schema, model_name)
                else:
                    field_type = dict

            elif json_type == "array":
                # Handle arrays; currently assuming array of objects or primitives
                item_schema = property_schema.get("items", {})
                if item_schema.get("type") == "object":
                    field_type = list[json_schema_to_model(item_schema, model_name)]
                else:
                    field_type = list
            if "default" in property_schema:
                field_default = property_schema["default"]
            if "description" in property_schema:
                field_description = property_schema["description"]
            if property_name in required_fields:
                required = True

        if required:
            fields[property_name] = (field_type, Field(description=field_description))
        else:
            fields[property_name] = (field_type, Field(default=field_default, description=field_description))

    # Handle additionalProperties
    if "additionalProperties" in schema:
        if schema["additionalProperties"] is True:
            config_extra = "allow"  # Allow additional properties
        elif schema["additionalProperties"] is False:
            config_extra = "forbid"  # Disallow additional properties
        elif isinstance(schema["additionalProperties"], dict):
            # If additionalProperties is a schema, allow and validate its type
            additional_model = json_schema_to_model(
                schema["additionalProperties"], f"{model_name}_AdditionalProperties"
            )
            fields["additional_properties"] = (dict[str, additional_model], {})

    # Create the model
    model = create_model(model_name, **fields)

    # Add custom Config class to handle extra properties
    class Config:
        extra = config_extra

    model.Config = Config

    return model
