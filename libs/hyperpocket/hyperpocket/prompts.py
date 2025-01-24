def pocket_extended_tool_description(description: str):
    return f"""
This tool functions as described in the <tool-description> XML tag:
<tool-description>
{description}
</tool-description>

Arguments required:
- 'thread_id': Chat thread ID (omit if unknown).
- 'profile': The profile of the user invoking the tool. (infer from messages; omit if unknown).
Users can request tools to be invoked in specific personas.
- 'body': Tool argument passed as a JSON 'body'.
"""
