# OpenAI

**OpenAI** is a widely used platform for language models like GPT-4. With Hyperpocket, you can extend OpenAI’s capabilities by integrating tools directly.

**Example: Using Hyperpocket with OpenAI**

```python
from openai import OpenAI
from hyperpocket_openai import PocketOpenAI
from hyperpocket.tool import from_git

# Load a tool
pocket = PocketOpenAI(
    tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/list-pull-requests",
    ]
)
tools = pocket.get_tools()
model = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

messages = []
while True:
    print("user input(q to quit) : ", end="")
    user_input = input()
    if user_input == "q":
        break

    user_message = {"content": user_input, "role": "user"}
    messages.append(user_message)

    while True:
        response = model.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tool_specs,
        )
        print(response)
```
