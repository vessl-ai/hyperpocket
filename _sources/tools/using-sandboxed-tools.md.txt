# Using Sandboxed Tools

With a sandboxed tool, an arbitrary code can be executed as a tool.
The code is executed on top of a container runtime, or WASM runtime.
Container runtime currently requires docker. Podman and other runtimes are planned to support.

The sandboxed tools takes tool input as standard input(stdin),
then returns output as standard output(stdout).
What your tool has to do is scan stdin (e.g. with `input()` for python),
and print out the result of your tool invocation (e.g. `print("success")` for python)

The sandboxed tools are actually a FunctionTool, wrapped with hyperdock packages.
For sandboxed tool, `hyperdock-container` or `hyperdock-wasm` might be used.

> Sandboxed tool running on WASM runtime has some unsupported features like L4 socket access or multithreading. Use at on your own risks.

## Referencing Tools from Local Directory

To integrate tools in your local directory, just pass Hyperpocket the absolute path to tool.
If the directory has a proper directory structure that Hyperpocket understands,
Hyperpocket will automatically integrate that tool.

```python
from hyperpocket_langchain import PocketLangchain

pocket = PocketLangchain(
    tools=[
        "/Users/possum/tools/slack/get-messages",
    ]
)
```

## Referencing Tools from Remote Git Repositories

You can copy and paste your GitHub url itself to load tools from a git repository.
When downloading the tool, your local gitconfig (probably `~/.gitconfig`) will be used.

### Putting GitHub URL

This feature is only supported for GitHub.

```python
from hyperpocket_langchain import PocketLangchain

pocket = PocketLangchain(
    tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
    ]
)

# ...
```

### Using `ContainerToolRequest` object

```python
from hyperpocket_langchain import PocketLangchain
from hyperdock_container.tool import ContainerToolRequest
from hyperdock_container.tool_reference import ContainerGitToolReference


pocket = PocketLangchain(tools=[
  ContainerToolRequest(
    tool_ref=ContainerGitToolReference(
      repository_url="https://some-private-git-repository.com/private/repo",
      git_ref="main",
    ),
    rel_path=""
  )
])

# ...
```

## Writing Your Own Sandboxed Tools

> More examples can be found in the [link](https://github.com/vessl-ai/hyperpocket/tree/main/tools)

Example structure for python tool is as follows:

```shell
/slack-get-messages
  /slack_get_messages
    /__init__.py
    /__main__.py
  /requirements.txt
  /pocket.json
```

- `pocket.json` must be present on the git repository, or local directory.
The file contains some crucial information to execute your code as a tool.
- The information specified in `pocket.json` is the followings:
  - Tool name, description, the JSON schema of the input argument (`.tool`)
  - Authentication handlers to use for a tool (`.auth`, for supported auth handlers, see [Auth](https://vessl-ai.github.io/hyperpocket/auth/supported-auth-list.html))
  - Language, or base image of a tool (`.language` or `.baseImage`)
    - For `.language == python`, `python:3.11-slim` image will be used as a base image.
    - For `.language == node`, `node` image will be used as a base image.
    - Otherwise, please specify `.baseImage`.
  - Build, run recipe for a tool (`.entrypoint`)
    - `.entrypoint.build` will be executed only once when you initialize your agent.
      - When initializing your tools, the container runtime will copy your code on the base image.
      - If `.entrypoint.build` is specified, the script will be executed.
      - After all initialization, the container snapshot will be committed on your local.
      - Installing requirements for your tool (e.g. `pip install -r requirements.txt`) will fit as a `.entrypoint.build` script.
    - `.entrypoint.run` will be executed whenever your agent calls the tool.
      - The script will run on top of the committed snapshot.
- Below is an example of a `pocket.json`. 
```json
{
  "tool": {
    "name": "slack_get_messages",
    "description": "get slack messages",
    "inputSchema": {
      "properties": {
        "channel": {
          "title": "Channel",
          "type": "string"
        },
        "limit": {
          "title": "Limit",
          "type": "integer"
        }
      },
      "required": [
        "channel",
        "limit"
      ],
      "title": "SlackGetMessageRequest",
      "type": "object"
    }
  },
  "auth": {
    "auth_provider": "slack",
    "scopes": ["channels:history"]
  },
  "language": "python",
  "entrypoint": {
    "build": "pip install -r requirements.txt",
    "run": "python slack_get_messages/__main__.py"
  }
}
```
