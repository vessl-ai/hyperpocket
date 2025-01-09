def pocket_extended_tool_description(description: str):
    return f'''
This tool performs as stated in the <tool-description></tool-description> XML tag.
<tool-description>
{description}
</tool-description>

This tool requires arguments as follows:
- 'thread_id': The ID of the chat thread where the tool is invoked. Omitted when unknown.
- 'profile': The profile of the user invoking the tool. Inferred from user's messages.
Users can request tools to be invoked in specific personas, which is called a profile.
If the user's profile name can be inferred from the query, pass it as a string in the 'profile' JSON property.
Omitted when unknown.
- 'body': The argument of the tool. The argument is passed as JSON property 'body' in the JSON schema.
'''
