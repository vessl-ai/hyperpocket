# Langgraph extensions

- Provide compatible tools in LangGraph
- Offer various methods for controlling authentication flow
    - [Multi-turn](#multi-turn)
    - [Human-in-the-loop](#human-in-the-loop-auth)

## Get Pocket Subgraph

```python


from hyperpocket_langgraph import PocketLanggraph

pocket = PocketLanggraph(tools=[
  "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
  "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
  "https://github.com/my-org/some-awesome-tool",
])

# get tool node from pocket
pocket_node = pocket.get_tool_node()
```

## Binding Pocket Tools

```python
import os

from langchain_openai import ChatOpenAI

from hyperpocket_langgraph import PocketLanggraph

pocket = PocketLanggraph(tools=[
  "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
  "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
])

# get tools from pocket to bind llm
tools = pocket.get_tools()
llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

# bind pocket tools with llm
llm_with_tools = llm.bind_tools(tools)
```

## Examples

```python
import os
from typing import Annotated

from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition
from typing_extensions import TypedDict

from hyperpocket_langgraph import PocketLanggraph

# Define pocket tools
pocket = PocketLanggraph(tools=[
  "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
  "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
])

# Get Pocket ToolNode
pocket_node = pocket.get_tool_node()


# Define your own langgraph state
class State(TypedDict):
  messages: Annotated[list, add_messages]


# Biding Pocket Tools
tools = pocket.get_tools()
llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
llm_with_tools = llm.bind_tools(tools)


# Make your langgraph with pocket nodes and bound llm
def chatbot(state: State):
  return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

# add pocket tool node
graph_builder.add_node("tools", pocket_node)

graph_builder.add_conditional_edges(
  "chatbot",
  tools_condition,
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
config = RunnableConfig(
  recursion_limit=30,
  configurable={"thread_id": "1"},  # edit thread_id by user if needed
)
```

## Authentication Flow Control

In Pocket, you can configure whether authentication operates in a multi-turn manner or as human-in-the-loop

by setting the `should_interrupt` flag when calling `get_tool_node`

### Multi-turn

Perform authentication in a multi-turn way

```python


from hyperpocket_langgraph import PocketLanggraph

# Define pocket tools
pocket = PocketLanggraph(tools=[
  "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
  "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
])

# Get Pocket ToolNode
pocket_node = pocket.get_tool_node(should_interrupt=False)  # multi turn 
```

### Human-in-the-loop Auth

```python


from hyperpocket_langgraph import PocketLanggraph

# Define pocket tools
pocket = PocketLanggraph(tools=[
  "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
  "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
])

# Get Pocket ToolNode
pocket_node = pocket.get_tool_node(should_interrupt=True)  # Human-in-the-loop 
```

### Differences between multi-turn and human-in-the-loop

The two approaches may not differ significantly in terms of user experience, but they are fundamentally distinct
internally.

In the case of the **multi-turn** way, the decision to return to an ongoing authentication(auth) flow is delegated to
the agent.

As a result, if the user want to cancel or modify the auth process midway, then **agent can adapt the
auth flow to incorporate those changes.**

<br>
However, with the human-in-the-loop way, it simply resumes from an interrupted point, proceeding directly with the
previous flow regardless of user input.

(Currently, users need to manually provide any input to move forward, but future updates aim to automate this transition
once the user's task is complete.)

Therefore, **in the human-in-the-loop way, users cannot modify or cancel the auth flow once it's resumed.**

<br>


That said, the multi-turn approach has its drawbacks as well. Since the agent determines whether to re-enter the auth
flow, there is a risk of incorrect decisions being made.

Conversely, the human-in-the-loop approach eliminates this risk by always continuing the previous flow as it is,
offering more predictable and controlled behavior for managing the auth flow.

