# Hyperdock for Langchain Community Tools

## But seriously, what is a Hyperdock?
- Hyperdock is just a fancy name for a collection of tools. Which are, just python functions returning `str`!
- In this case, the collection will contain functions that invoke tools extending `BaseTool` interface of langchain.

## How to use it?
- To use tools from `langchain-community`, install langchain-community first.
```bash
$ pip install langchain-community # or maybe uv add langchain-community
```
- Some tool might require additional dependencies. For example, slack tools of langchain-community requires `slack-sdk`. Check the requirements of the tool, and install them as well.
- Make a dock with the tools you want to use. For example, let's say you want to use `DuckDuckGoSearchRun` tool.
```python
from hyperdock_langchain import dock as langchain_dock, LangchainToolRequest
from langchain_community.tools import DuckDuckGoSearchRun

# ... 
dock = langchain_dock(
    LangchainToolRequest(tool_type=DuckDuckGoSearchRun), # you should pass the tool type, not a tool instance.
    # ...
)
```
- You might want to use hyperpocket's auth feature while using the langchain tools. In that case, you can define `auth` property for the `LangchainToolRequest`.
- The auth property must be possible to serialized as [`hyperpocket.tool.ToolAuth`](https://vessl-ai.github.io/hyperpocket/autoapi/libs/hyperpocket/hyperpocket/tool/tool/index.html#libs.hyperpocket.hyperpocket.tool.tool.ToolAuth).
```python
from hyperdock_langchain import dock as langchain_dock, LangchainToolRequest
from langchain_community.tools import SlackGetMessage

# ... 
dock = langchain_dock(
    LangchainToolRequest(tool_type=SlackGetMessage, auth={"auth_provider": "slack"}),
    # ...
)
```
- If auth is provided, this dock recognize the credentials generated and set them as a proper environment variable.
- After you make your dock, call from_dock from your pocket instantiation. For example, Let's say you're using hyperpocket for langchain. You can do:
```python
from hyperpocket.tool import from_dock
from hyperpocket_langchain import PocketLangchain
from hyperdock_langchain import dock as langchain_dock, LangchainToolRequest

dock = langchain_dock(
    #...
)
# ...
def agent():
    # ...
    # initialize the pocket
    pocket = PocketLangchain(
        tools=[
            *from_dock(dock),
        ]
    )
```
