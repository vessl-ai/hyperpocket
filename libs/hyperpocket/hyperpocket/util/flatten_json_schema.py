import copy


def flatten_json_schema(schema: dict):
    """
    Flatten JSON Schema by resolving all $refs using definitions in $defs
    and convert to a fully nested schema.
    """
    definitions = schema.get("$defs", {})
    schema_copy = copy.deepcopy(schema)

    # Resolve references within $defs first
    resolved_definitions = {}
    for key, value in definitions.items():
        resolved_definitions[key] = resolve_refs(value, definitions)

    # Resolve references in the main schema
    schema_copy.pop("$defs", None)  # Remove $defs
    return resolve_refs(schema_copy, resolved_definitions)


def resolve_refs(schema, definitions):
    """
    Recursively resolve $ref references within the schema using $defs.
    """
    if isinstance(schema, dict):
        # Recursively check nested dictionaries
        resolved_schema = {}
        for key, value in schema.items():
            # If $ref exists, resolve the reference
            if key == "$ref":
                ref_path = schema["$ref"]
                ref_name = ref_path.split("/")[
                    -1
                ]  # Extract the reference name from $defs/Req -> Req
                resolved = definitions.get(ref_name)
                if resolved:
                    resolved_schema |= resolve_refs(
                        copy.deepcopy(resolved), definitions
                    )
            else:
                resolved_schema[key] = resolve_refs(value, definitions)
        return resolved_schema

    elif isinstance(schema, list):
        # Recursively resolve references in list items
        return [resolve_refs(item, definitions) for item in schema]

    return schema
