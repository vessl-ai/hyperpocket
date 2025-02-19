# Anthropic

**Anthropic** provides advanced language model capabilities with its Claude models. Hyperpocket tools can be integrated for dynamic actions.

**Example: Using Anthropic with Tool Calling**

```python
from anthropic import Anthropic
from hyperpocket_anthropic import PocketAnthropic

# Initialize Anthropic LLM
client = Anthropic(api_key="YOUR_ANTHROPIC_API_KEY")

# Load a Hyperpocket tool
pocket = PocketAnthropic(
    tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/insert-calendar-events",
    ]
)

tool_specs = pocket.get_anthropic_tool_specs()

messages = []
while True:
    user_input = input()
    messages.append({"role": "user", "content": user_input})

    while True:
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=500,
            messages=messages,
            tools=tool_specs,
        )

        messages.append({"role": "assistant", "content": response.content})

        print(response)
```
