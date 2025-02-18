# Hyperdock for LlamaIndex Tools

## But seriously, what is a Hyperdock?

- Hyperdock is just a fancy name for a collection of tools. Which are, just python functions returning `str`!
- In this case, the collection will contain functions that invoke tools which are methods of subclass of `BaseToolSpec` from llamaindex.

## How to use it?

- To use tools from `llama-index`, install independent tool package first.

```bash
$ pip install llama-index-tools-duckduckgo # or maybe uv add llama-index-tools-duckduckgo
```

- Make a dock with the tools you want to use. For example, let's say you want to use `DuckDuckGoSearchRun` tool.

```python
from hyperdock_llamaindex import LlamaIndexToolRequest, dock as llamaindex_dock
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec

# ...
dock = llamaindex_dock(
        LlamaIndexToolRequest(
            tool_func=DuckDuckGoSearchToolSpec.duckduckgo_full_search,
            tool_args={
                "max_results": 10,
            },
        )
    )
```

- You might want to use hyperpocket's auth feature while using the llamaindex tools. In that case, you can define `auth` property for the `LlamaIndexToolRequest`.
- The auth property must be possible to serialized as [`hyperpocket.tool.ToolAuth`](https://vessl-ai.github.io/hyperpocket/autoapi/libs/hyperpocket/hyperpocket/tool/tool/index.html#libs.hyperpocket.hyperpocket.tool.tool.ToolAuth).

- After you make your dock, call from_dock from your pocket instantiation. For example, Let's say you're using hyperpocket for llamaindex. You can do:

```python
from hyperpocket.tool import from_dock
from hyperpocket_llamaindex import PocketLlamaindex
from hyperdock_llamaindex import LlamaIndexToolRequest, dock as llamaindex_dock

dock = llamaindex_dock(
    #...
)
# ...
def agent():
    # ...
    # initialize the pocket
    pocket = PocketLlamaindex(
        tools=[
            *from_dock(dock),
        ]
    )
```
