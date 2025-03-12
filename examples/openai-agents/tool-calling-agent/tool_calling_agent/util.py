from agents import FunctionTool

def convert_to_openai_agent_tool(spec):
    spec["function"]["parameters"]["additionalProperties"] = False
    if "properties" in spec["function"]["parameters"]:
        properties = spec["function"]["parameters"]["properties"]
        spec["function"]["parameters"]["required"] = list(properties.keys())
        for prop in properties.values():
            if "default" in prop:
                del prop["default"]
    
    tool = FunctionTool(
        name=spec["function"]["name"],
        description=spec["function"]["description"],
        params_json_schema=spec["function"]["parameters"],
        on_invoke_tool=spec["callable"]
    )
    
    return tool