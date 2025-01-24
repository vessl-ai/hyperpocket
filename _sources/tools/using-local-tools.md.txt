# Using Local Tools

## Local Tool

A **Local Tool** in Hyperpocket is a tool you can write locally on your environment and can be run on a isolated \*
\*WebAssembly (WASM)\*\*.

Local tools are used to run custom logic or tools that are not available in git tools.

But for the most part, you will be enough with git tools or function tools.

You will want to use local tools in the following cases:

- Utilizing other languages than Python: If a tool's language is supported by WASM, you can run it as a local tool.
- (Coming soon) Ejecting git tools for customizing: You can eject a git tool and customize it as a local tool. (This feature is coming soon.)

Go to the bottom of the guide to see a detailed example.

## How it works

Similar to git tools, but it loads code from your local directory.

See [(TBU) How tools are loaded](tbd) for more details.

## Guides

### Define a Local Tool

Ensure the tool is structured with the required configuration files (e.g., schema.json, config.toml).

Example structure for python tool is as follows:

```shell
/local-tool
  /local-tool
    /__init__.py
    /__main__.py
  /config.toml
  /schema.json
```

- `__init__.py`: The entry point of the tool.
- `__main__.py`: The main logic of the tool.
- `config.toml`: The configuration file for the tool.

  ```toml
  name = "local-tool"
  description = "description of the tool"
  language = "python" # or else

  [auth]
  auth_provider = "github" # example, or else
  scopes = ["repo"] # different by auth provider
  ```

- `schema.json`: The schema of the argument for the tool. This is used for defining pydantic model and also used as tool specs for LLMs.

  ```json
  {
    "properties": {
      "arg1": {
        "type": "string"
      },
      "arg2": {
        "type": "number"
      }
    },
    "required": ["arg1", "arg2"]
  }
  ```

### Load and use the Local Tool

Use the `from_local` function to load a tool from a specified path.

Example Code: Loading a Local Tool

```python
from hyperpocket_openai import PocketOpenAI
from hyperpocket.tool import from_local

pocket = PocketOpenAI(
    tools=[from_local("/path/to/local/tool")]
)

# And more ...
```
