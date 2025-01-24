# Using Git Tools

## Git Tools

A **Git Tool** is a tool that is fetched from remote git repositories and run on WASM runtime.

## How to Use Git Tools

You can copy and paste your git url itself, or use `from_git` function to load tools from a git repository.

### Simply putting git URL

```python
from hyperpocket_langchain import PocketLangchain

pocket = PocketLangchain(
    tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
    ]
)

# ...
```

### `from_git` function

```python
from hyperpocket_langchain import PocketLangchain
from hyperpocket.tool import from_git


pocket = PocketLangchain(tools=[from_git(
    repository="https://github.com/vessl-ai/hyperpocket",
    ref="main",
    rel_path="tools/slack/get-message"
)])

# ...
```

## Advanced - Structure of a Git Tool Repository

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
