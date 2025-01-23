# LangGraph

**LangGraph** supports graph-based workflows for language models. With Hyperpocket, you can integrate tools for more structured and complex workflows.

**Example: Using LangGraph with Slack Integration**

```python
from hyperpocket.tool import from_git
from langgraph import AgentGraph

# Load tools with Hyperpocket
tool = from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/schedule-message")

# Define the LangGraph workflow
graph = AgentGraph()
graph.add_node("schedule_message", tool)
graph.connect("start", "schedule_message")
graph.connect("schedule_message", "end")

# Execute the workflow
graph.execute({"channel": "general", "message": "Team meeting at 3 PM"})
```