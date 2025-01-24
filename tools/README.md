## Tool Examples

### Config.toml

- name(str) : tool name
- description(str) : tool description
- auth_handlers(list[str]) : auth_handlers name list
- auth_scopes(dict[str, list[str]]) : auth_scopes per auth_handler
- tool_vars(dict[str, str]) : tool variables to use in tool

**example**

```toml
name = "slack_get_messages"
description = "get slack messages"
auth_handlers = ["slack-oauth2"]

[auth_scopes]
slack = ["channels:history"]

[tool_vars]
a = "1"
b = "2"
```

- you can access `tool_vars` values in your tool code
    - in wasm tool, you can access this values via `environment variables`
    - in function tool, you can access this values via `kwargs`

### schema.json

open ai spec schema json

**example**

```
{
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
```

### dist

requirements to execute your code in independent runtime

### Example using uv

```shell
uv init <your-tool-name>
uv add pydantic --raw-sources # if you need to install pydantic, should use this command.
# ...

uv build
```

- When uploading your tool to github, make sure to remove `dist` from `.gitignore`.

### `__main__.py`

your own code to execute

🚨 input : stdin

🚨 output : stdout

🚨 auth : environment variables

🚨🚨 should call your code in `if __name__ == '__main__': ..`

**example**

```python
import json
import os
import sys
from typing import Tuple, List

from pydantic import BaseModel, Field
from slack_sdk import WebClient

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN", ""))


class SlackGetMessageRequest(BaseModel):
    channel: str
    limit: int = Field(default=10)


def get_channel() -> List[Tuple[str, str]]:
    conversation_list = client.conversations_list(limit=500)
    channels = []
    for channel in conversation_list.get("channels", []):
        channels.append((channel["id"], channel["name"]))

    return channels


def get_channel_id_by_name(channel_name: str) -> str:
    channels = get_channel()
    for id, name in channels:
        if name == channel_name:
            return id


def get_messages(req: SlackGetMessageRequest):
    channel_id = get_channel_id_by_name(channel_name=req.channel)
    response = client.conversations_history(channel=channel_id, limit=req.limit)
    return response


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = SlackGetMessageRequest.model_validate(req)
    if req_typed.channel[0] == "#":
        req_typed.channel = req_typed.channel[1:]

    response = get_messages(req_typed)

    print(response)


if __name__ == '__main__':
    main()
```

### `__init__.py`

define your `main()` function to `__all__`

```python
from your_tool.__main__ import main

__all__ = ['main']
```