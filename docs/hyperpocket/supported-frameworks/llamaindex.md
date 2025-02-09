# LlamaIndex

**LlamaIndex** allows language models to interact with structured data. Hyperpocket tools can be integrated for retrieving and managing data dynamically.

**Example: Using LlamaIndex with Hyperpocket Tools**

```python
from llama_index.core.agent import AgentRunner, FunctionCallingAgent
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI

from hyperpocket.tool import from_git
from hyperpocket_llamaindex import PocketLlamaindex

llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load a tool
pocket = PocketLlamaindex(
    tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/list-pull-requests",
    ]
)
tools = pocket.get_tools()

memory = ChatMemoryBuffer.from_defaults(chat_history=[], llm=llm)

agent = FunctionCallingAgent.from_tools(
    tools=tools, llm=llm, memory=memory, verbose=True
)

while True:
    user_input = input()
    if user_input == "q":
        break

    agent.chat(user_input)
```
