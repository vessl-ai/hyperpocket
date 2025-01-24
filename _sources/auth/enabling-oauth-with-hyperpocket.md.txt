# Enabling OAuth with Hyperpocket

Hyperpocket simplifies the integration of OAuth-based authentication, making it easy to handle multi-step flows
securely.

OAuth is particularly useful for tools that require user authorization, such as Slack, GitHub, or Google APIs.

## **How to Apply OAuth in Hyperpocket**

### Hyperpocket WasmTool

#### 1. Set the OAuth Configuration

Set a oauth configuration. it varies by Oauth Provider

Example(Slack):

```toml
[auth.slack]
client_id = "<YOUR_GOOGLE_APP_CLIENT_ID>"
client_secret = "<YOUR_GOOGLE_APP_CLIENT_SECRET>"
```

#### 2. Define `wasm-tool-path/config.toml` in your wasm tool

- Add fields about authentication to `config.toml`

```toml
name = "slack_get_messages"
description = "get slack messages"
language = "python"

# needed fields for authentication
[auth]
auth_provider = "slack"
scopes = ["channels:history"]
```

#### 3. Plug in the tool in Hyperpocket`

```python
pocket = Pocket(tools=["your/local/auth/tool/path"])
# or
pocket = Pocket(tools=["https://github.com/your-organizaion/your-repository"])
```

#### 4. Invoke tool with authentication

```python
# initialize tool authentication.
authentication_url = await pocket.initialize_tool_auth()

# send this authentication_url to user.
print(authentication_url)

# wait for your authentication process.
await pocket.wait_tool_auth()

# invoke tool and get result
result = pocket.invoke(
    tool_name="get_slack_messages",
    body={
        "channel": "<YOUR_CHANNEL>",
        "limit": 10}
)
```

#### Full code

```python
import asyncio

from hyperpocket import Pocket


async def main():
    # init pocket with your tool.
    pocket = Pocket(tools=["https://github.com/your-organizaion/your-repository"])

    # initialize tool authentication.
    authentication_url = await pocket.initialize_tool_auth()

    # send this authentication_url to user.
    print(authentication_url)

    # wait for your authentication process.
    await pocket.wait_tool_auth()

    # invoke tool and get result
    result = pocket.invoke(
        tool_name="get_slack_messages",
        body={
            "channel": "<YOUR_CHANNEL>",
            "limit": 10}
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

### Hyperpocket FunctionTool

#### 1. Set the OAuth Configuration

Set a oauth configuration. it varies by Oauth Provider

Example(Slack):

```toml
[auth.slack]
client_id = "<YOUR_GOOGLE_APP_CLIENT_ID>"
client_secret = "<YOUR_GOOGLE_APP_CLIENT_SECRET>"
```

#### 2. Define the Tool

Use the `@function_tool` decorator to create a tool with the OAuth configuration.

Example(Slack):

Here’s how to define and use a Google tool with OAuth authentication:

```python
from slack_sdk import WebClient

from hyperpocket.auth import AuthProvider
from hyperpocket.tool import function_tool


@function_tool(
    auth_provider=AuthProvider.SLACK,
    scopes=["channels:history", "im:history", "mpim:history", "groups:history", "mpim:read", "im:read"])
def slack_get_messages(channel: str, limit: int = 10, **kwargs) -> list:
    """
    Get recent messages from a Slack channel.
    
    Args:
        channel(str): slack channel to be fetched
        limit(int): maximum message limit 
    """
    client = WebClient(token=kwargs["SLACK_BOT_TOKEN"])
    response = client.conversations_history(channel=channel, limit=limit)
    return list(response)
```

- `auth_provider`: Define which authentication provider token is needed in your tool
- `scopes`: needed authentication scopes in your tool

#### 3. Plug in the tool in Hyperpocket`

```python
from hyperpocket import Pocket

pocket = Pocket(tools=[slack_get_messages])
```

#### 4. Invoke tool with authentication

```python
# initialize tool authentication.
authentication_url = await pocket.initialize_tool_auth()

# send this authentication_url to user.
print(authentication_url)

# wait for your authentication process.
await pocket.wait_tool_auth()

# invoke tool and get result
result = pocket.invoke(
    tool_name="get_slack_messages",
    body={
        "channel": "<YOUR_CHANNEL>",
        "limit": 10}
)
```

### Full code

```python
import asyncio

from slack_sdk import WebClient

from hyperpocket import Pocket
from hyperpocket.auth import AuthProvider
from hyperpocket.tool import function_tool


@function_tool(
    auth_provider=AuthProvider.SLACK,
    scopes=["channels:history", "im:history", "mpim:history", "groups:history", "mpim:read", "im:read"])
def slack_get_messages(channel: str, limit: int = 10, **kwargs) -> list:
    """
    Get recent messages from a Slack channel.
    
    Args:
        channel(str): slack channel to be fetched
        limit(int): maximum message limit 
    """
    client = WebClient(token=kwargs["SLACK_BOT_TOKEN"])
    response = client.conversations_history(channel=channel, limit=limit)
    return list(response)


async def main():
    # init pocket with your tool.
    pocket = Pocket(tools=[slack_get_messages])

    # initialize tool authentication.
    authentication_url = await pocket.initialize_tool_auth()

    # send this authentication_url to user.
    print(authentication_url)

    # wait for your authentication process.
    await pocket.wait_tool_auth()

    # invoke tool and get result
    result = pocket.invoke(
        tool_name="get_slack_messages",
        body={
            "channel": "<YOUR_CHANNEL>",
            "limit": 10}
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

## Why Use OAuth with Hyperpocket?

- **Dynamic Token Management:** Handles token issuance, storage, and refresh cycles internally.
- **Secure Authentication:** No exposure of sensitive credentials like access tokens.
- **Seamless Integration:** Easily integrate OAuth flows into multi-turn workflows.