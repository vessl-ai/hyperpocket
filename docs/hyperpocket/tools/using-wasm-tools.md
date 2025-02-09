# Using WASM Tools

> WASM Tools has some unsupported features like L4 socket access or multithreading. Use at on your own risks.

## Referencing Tools from Local Directory

To integrate tools in your local directory, just pass Hyperpocket the absolute path to tool.
If the directory has a proper directory structure that Hyperpocket understands,
Hyperpocket will automatically integrate that tool.

```python
from hyperpocket_langchain import PocketLangchain

pocket = PocketLangchain(
    tools=[
        /Users/possum/tools/slack/get-messages",
    ]
)
```

## Referencing Tools from Remote Git Repositories

You can copy and paste your GitHub url itself, or use `from_git` function to load tools from a git repository.
When downloading the tool, your local gitconfig (probably `~/.gitconfig`) will be used.

### Simply putting GitHub URL

This simple feature is only supported for GitHub.

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

## Example Directory Structure of a WASM Tool with Python

> More examples can be found in the [link](https://github.com/vessl-ai/hyperpocket/tree/main/tools)

Ensure the tool is structured with the required configuration files (e.g., schema.json, config.toml).


Example structure for python tool is as follows:

```shell
/git-tool
  /git-tool
    /__init__.py
    /__main__.py
  /config.toml
  /schema.json
```

- `__init__.py`: The entry point of the tool. This should export the main function.
```python
from git_tool.__main__ import main
__all__ = ["main"]

```
- `__main__.py`: The main logic of the tool. Note that main function should be defined here.
```python
import json, os


def main():
    req = json.load(sys.stdin.buffer)
    print(f"{req["a"]} + {req["b"]} = {req["a"] + req["b"]}")

if __name__ == '__main__':
    main()
```
- `config.toml`: The configuration file for the tool.

```toml
name = "git-tool"
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
