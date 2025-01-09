## Anthropic extensions

### Get Pocket Tools

```python
import hyperpocket as pk
from pocket_llamaindex import PocketLlamaindex

# 
pocket = PocketLlamaindex(tools=[
    *pk.curated_tools.SLACK,  # SLACK = [slack_get_message, slack_post_message, ..]
    *pk.curated_tools.LINEAR,
    "https://github.com/my-org/some-awesome-tool"]
)

# get tools from pocket
tools = pocket.get_tools()
```


### Examples

```python
from llama_index.core.agent import FunctionCallingAgent
from llama_index.llms.openai import OpenAI

import hyperpocket as pk
from pocket_llamaindex import PocketLlamaindex

pocket = PocketLlamaindex(tools=[
    *pk.curated_tools.SLACK,  # SLACK = [slack_get_message, slack_post_message, ..]
    *pk.curated_tools.LINEAR,
    "https://github.com/my-org/some-awesome-tool"]
)

# get tools from pocket
tools = pocket.get_tools()

llm = OpenAI()
# pass tools get by pocket to an argument
agent = FunctionCallingAgent.from_tools(
    tools=tools, llm=llm, verbose=True
)
```