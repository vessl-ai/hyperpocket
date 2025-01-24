# Integration from Git

## **What is a Git-Integrated WASM Tool?**

A **Git-Integrated WASM Tool** is a WebAssembly-based tool that is fetched directly from a Git(Github, GitLab,
BitBucket, ...) repository.

This allows developers to maintain tools remotely and integrate them seamlessly into
Hyperpocket workflows.

## **How to Use Git-Integrated WASM Tools**

Hyperpocket provides the `from_git` function to load tools from a Git repository. Here’s how it works:

1. **Repository URL:** Specify the Git repository where the tool is hosted.

2. **Branch/Tag (ref):** Define the Git reference (branch or tag) to use.

3. **Relative Path:** Specify the tool’s path within the repository.

**Code Example: Loading a Git Tool**

```python
from hyperpocket import Pocket
from hyperpocket.tool.wasm.tool import from_git

tools = [from_git(
    repository="https://github.com/vessl-ai/hyperpocket",
    ref="main",
    rel_path="tools/slack/get-message"
)]

pocket = Pocket(tools=tools)

# ...
```

Or you can just put **Github URL** on the Hyperpocket.

```python
from hyperpocket import Pocket

tools = ["https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages"]
pocket = Pocket(tools=tools)
```

## **Executing a Git Tool**

Once the tool is loaded, create an instance of the WasmTool class and execute the tool using the invoke method.

**Code Example: Executing a Git Tool**

```python
from hyperpocket import Pocket

if __name__ == '__main__':
    # Write Github URL in tools
    tools = [
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/none/simple-echo-tool"
    ]

    # Create Pocket
    pocket = Pocket(tools=tools)

    # Execute the tool
    result = pocket.invoke(
        tool_name="simple_echo_text",
        body={
            "text": "hello"
        }
    )
    print(result)  # Output: JSON response from the tool
```

**Structure of a Git Tool Repository**

The tool repository must include the following:

1. config.toml**:** Defines tool metadata and runtime.

• Example:

```toml
name = "Slack Get Message Tool"
description = "Fetch messages from a Slack channel."
language = "python"
```

2. schema.json**:** Defines the input/output schema for the tool.

• Example:

```json
{
  "type": "object",
  "properties": {
    "channel": {
      "type": "string"
    },
    "limit": {
      "type": "integer"
    }
  },
  "required": [
    "channel",
    "limit"
  ]
}
```

3. **Tool Script:** The logic for the tool and `dist` file, e.g., a Python script to interact with the Slack API.

## **When to Use Git-Integrated WASM Tools**

Use Git tools when:

•    **Remote Management is Preferred:** Tools are centrally stored and updated in a repository.

•    **Collaboration is Key:** Multiple developers can contribute and improve tools.

•    **Version Control is Necessary:** Git’s branching and versioning simplify tool updates and testing.