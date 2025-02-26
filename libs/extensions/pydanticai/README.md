## PydanticAI extensions

### Binding Pocket Tools

```python
from hyperpocket_pydanticai import PocketPydanticAI

pocket = PocketPydanticAI(tools=[
    "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
    "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
])
# get langchain compatible tools from pocket
tools = pocket.get_tools()

# get agent 
agent = Agent(
    "openai:gpt-4o",
    system_prompt="You are a slack messaging assistant. You can help the user by calling proper tools",
    tools=tools,
)
```
