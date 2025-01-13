## Anthropic extensions

### Get Pocket Anthropic Tool Spec

```python
from hyperpocket.tool import from_git

from hyperpocket_anthropic import PocketAnthropic

pocket = PocketAnthropic(tools=[
    "https://github.com/my-org/some-awesome-tool",
    from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
    from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
]
)

# get anthropic compatible tool specs from pocket 
tool_specs = pocket.get_anthropic_tool_specs()
```


### Tool Injection

```python
import os

from anthropic import Anthropic

messages = [
    {
        "role": "user",
        "content": "get slack message",
    }
]

llm = Anthropic()
response = llm.messages.create(
    model=os.getenv("ANTHROPIC_MODEL_NAME"),
    max_tokens=500,
    messages=messages,
    tools=tool_specs,  # pass the tool specs as an tools argument
)
```


### Tool Call

```python
response = llm.messages.create(
    model=os.getenv("ANTHROPIC_MODEL_NAME"),
    max_tokens=500,
    messages=messages,
    tools=tool_specs,  # pass the tool specs as an tools argument
)

tool_result_blocks = []
for block in response.content:
    if block.type == "tool_use":
        tool_result_block = pocket.invoke(block)
        tool_result_blocks.append(tool_result_block)

messages.append({"role": "user", "content": tool_result_blocks})

response_after_tool_call = llm.messages.create(
    model=os.getenv("ANTHROPIC_MODEL_NAME"),
    max_tokens=500,
    messages=messages,
    tools=tool_specs,  # pass the tool specs as an tools argument
)

# ...
```

### Full Code

```python
import os

from anthropic import Anthropic
from hyperpocket.tool import from_git

from hyperpocket_anthropic import PocketAnthropic

pocket = PocketAnthropic(tools=[
    "https://github.com/my-org/some-awesome-tool",
    from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
    from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
]
)

# get anthropic compatible tool specs from pocket 
tool_specs = pocket.get_anthropic_tool_specs()
messages = [
    {
        "role": "user",
        "content": "get slack message",
    }
]

llm = Anthropic()
response = llm.messages.create(
    model=os.getenv("ANTHROPIC_MODEL_NAME"),
    max_tokens=500,
    messages=messages,
    tools=tool_specs,  # pass the tool specs as an tools argument
)

tool_result_blocks = []
for block in response.content:
    if block.type == "tool_use":
        tool_result_block = pocket.invoke(block)  # tool call by pocket
        tool_result_blocks.append(tool_result_block)

messages.append({"role": "user", "content": tool_result_blocks})

response_after_tool_call = llm.messages.create(
    model=os.getenv("ANTHROPIC_MODEL_NAME"),
    max_tokens=500,
    messages=messages,
    tools=tool_specs,  # pass the tool specs as an tools argument
)

```


### Examples

```python
import os

from anthropic import Anthropic
from hyperpocket.tool import from_git

from hyperpocket_anthropic import PocketAnthropic

client = Anthropic()
pocket = PocketAnthropic(tools=[
    "https://github.com/my-org/some-awesome-tool",
    from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
    from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
]
)

tool_specs = pocket.get_anthropic_tool_specs()

messages = []
while True:
    print("user(q to quit) : ", end="")
    user_input = input()
    if user_input == "q":
        break
    if user_input == "":
        continue

    messages.append({"role": "user", "content": user_input})

    while True:
        response = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL_NAME"),
            max_tokens=500,
            messages=messages,
            tools=tool_specs,
        )

        messages.append({"role": "assistant", "content": response.content})

        tool_result_blocks = []
        for block in response.content:
            if block.type == "text":
                print("[ai] response : ", block.text)

            elif block.type == "tool_use":
                tool_result_block = pocket.invoke(block)
                tool_result_blocks.append(tool_result_block)

                print("[tool] response : ", tool_result_block["content"])

        messages.append({"role": "user", "content": tool_result_blocks})

        if response.stop_reason != "tool_use":
            break
```