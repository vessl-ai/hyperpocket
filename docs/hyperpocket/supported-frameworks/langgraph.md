# LangGraph

**LangGraph** supports graph-based workflows for language models. With Hyperpocket, you can integrate tools for more structured and complex workflows.

**Example: Using LangGraph with Slack Integration**

```python
from hyperpocket.tool import from_git
from hyperpocket_langgraph import PocketLanggraph
from langgraph import AgentGraph

# Load tools with Hyperpocket
pocket = PocketLanggraph(tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/list-pull-requests",
    ])

# Define the LangGraph workflow
graph = AgentGraph()
graph.add_node("schedule_message", pocket.get_tool_node(should_interrupt=True))
graph.connect("start", "schedule_message")
graph.connect("schedule_message", "end")

# Execute the workflow
graph.execute({"channel": "general", "message": "Team meeting at 3 PM"})
```
