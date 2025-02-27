## Gemini extensions

### Binding Pocket Tools

```python
import os

from google import genai
from google.genai import types

from hyperpocket_gemini import PocketGemini

pocket = PocketGemini(tools=[
    "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
    "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
])

# get gemini compatible tools from pocket
tools = pocket.get_gemini_tool_specs()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
messages = []  # add system prompt here. 

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=messages,
    config=types.GenerateContentConfig(tools=tools)
)
```

### Agent Examples

- See here: [link](/examples/gemini/tool-calling-agent/tool_calling_agent/agent.py)
