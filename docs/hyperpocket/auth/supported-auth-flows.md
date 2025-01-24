# Supported Auth flows

**What is Hyperpocket Auth?**

Hyperpocket provides a robust and flexible authentication flow to support secure interactions with external tools and APIs. It enables **multi-turn authentication**, ensures the safety of sensitive data, and integrates seamlessly with various AI agent frameworks. By supporting multiple authentication scenarios, Hyperpocket removes the need for static user credentials and provides dynamic, secure authentication tailored to different workflows.

## **🔹 Authentication Features**

### 1. **Multi-Turn Authentication**

- Supports complex, multi-step authentication scenarios (e.g., OAuth flows).
- Memory-enabled workflows allow AI agents to complete authentication over multiple interactions.
- Allows tools to initialize authentication in advance, reducing latency during actual usage.

Example: Logging into multiple Slack accounts across different organizations.

### 2. **Secure Internal Auth Server**

- An internal authentication server is initialized during Hyperpocket setup.
- Handles OAuth callbacks and issues access tokens securely without exposing authentication codes or tokens to external systems.
- Tokens and sensitive data are stored internally, ensuring no external leaks.

### 3. **Profile-Based Auth**

- Defines “Profiles” to allow users to manage multiple personas within the same thread.

Example: A user can authenticate with multiple accounts (e.g., A’s Slack and B’s Slack) simultaneously.

### 4. **Wide Language Support**

- Supports tools written in multiple programming languages (e.g., Python, JavaScript).
- Auth flows are compatible across different tool implementations.

### 5. **Tool-Level Isolation**

- Each tool operates in its isolated WASM runtime, ensuring no dependency conflicts.
- Tokens and environment variables are passed securely to each tool.

### 6. **Interrupt-Based Flows**

- Supports interrupt-based workflows where tools can be called without requiring a full multi-turn session.
- Ideal for lightweight, single-step operations.

## **🔹 Why Hyperpocket Auth Stands Out**

- **Dynamic and Flexible**
  - Unlike static user authentication, Hyperpocket adapts to dynamic scenarios, making it suitable for diverse agent frameworks.
- **Enhanced Security**
  - Access tokens and authentication codes are securely managed within Hyperpocket’s environment.
- No external exposure of sensitive credentials.
  - **Seamless Integration**
- No need for additional server setup; the internal auth server handles all token issuance and management.
- Compatible with various agent frameworks like LangChain or custom implementations.
- **Multi-Account Support**
- A single user can authenticate with multiple accounts (e.g., multiple Slack workspaces or GitHub organizations).

## **🔹 Code Example: OAuth Integration**

Here’s an example of how Hyperpocket handles an OAuth-based tool with multi-turn authentication:

```python
from slack_sdk import WebClient

from hyperpocket.auth import AuthProvider
from hyperpocket.tool import function_tool

# Define a tool with OAuth authentication
@function_tool(
    auth_provider=AuthProvider.SLACK,
    scopes=["channels:history", "im:history", "mpim:history", "groups:history", "reactions:read", "mpim:read",
            "im:read"]
)
def get_slack_messages(channel: str, limit: int, **kwargs) -> list:
    """
    Fetch recent messages from a Slack channel.

    channel(str): slack channel name
    limit(int): message limit
    """

    token = kwargs["SLACK_BOT_TOKEN"]
    client = WebClient(token=token)

    # do something you need
    response = client.conversations_history(channel=channel, limit=limit)

    return list(response)

from hyperpocket.tool import tool
from hyperpocket.auth import OAuthHandler

# Define a tool with OAuth authentication
@tool(auth=OAuthHandler(
    client_id="your_client_id",
    client_secret="your_client_secret",
    scopes=["read:messages", "write:messages"],
    auth_url="https://slack.com/oauth/authorize",
    token_url="https://slack.com/api/oauth.access"
))
def get_slack_messages(channel: str, limit: int) -> list:
    """Fetch recent messages from a Slack channel."""
		messages = []
		# do somethin return [{"user": "Alice", "message": "Hello!"}, {"user": "Bob", "message": "Hi!"}]

# Example usage
if __name__ == "__main__":

    messages = get_slack_messages(channel="general", limit=10)
    print(messages)
```

## **🔹 Code Example: Initializing authentication in advance **

Here’s an example of how to set up authentication in the initial phase, making it unnecessary for the user to proceed through complex authentication steps.

```python
import asyncio

from hyperpocket import Pocket
from hyperpocket.auth import AuthProvider
from hyperpocket.tool import function_tool


# before starting, set slack, google oauth client id/secret in pocket setting.toml

@function_tool(
    auth_provider=AuthProvider.SLACK
)
def function_tool_with_slack_auth(**kwargs):
    """
    function tool with slack auth
    """
    # do something with SLACK_BOT_TOKEN ..

    return "success to test slack"


@function_tool(
    auth_provider=AuthProvider.GOOGLE,
    scopes=["https://www.googleapis.com/auth/calendar"]
)
def function_tool_with_google_auth(**kwargs):
    """
    function tool with google auth
    """
    # do something with GOOGLE_TOKEN

    return "success to test google"


async def main():
    pocket = Pocket(
        tools=[
            function_tool_with_slack_auth,
            function_tool_with_google_auth,
        ]
    )

    # 01. get authenticatio URI
    prepare_list = await pocket.initialize_tool_auth()

    for idx, prepare in enumerate(prepare_list):
        print(f"{idx + 1}. {prepare}")

    # 02. wait until auth is done
    await pocket.wait_tool_auth()

    # 03. tool invoke without interrupt
    slack_auth_function_result = await pocket.ainvoke(tool_name="function_tool_with_slack_auth", body={})
    google_auth_function_result = await pocket.ainvoke(tool_name="function_tool_with_google_auth", body={})

    print("slack auth function result: ", slack_auth_function_result)
    print("google auth function result: ", google_auth_function_result)


if __name__ == "__main__":
    asyncio.run(main())
```

## **🔹 Supported Authentication Scenarios**

Hyperpocket’s auth system supports a wide range of scenarios, including:

- **OAuth 2.0 Flows:** Token issuance, callback handling, and multi-account support.
- **Environment-Based Auth:** Tokens and static information passed securely as environment variables.

• **Multi-Profile Management:** Manage multiple tokens for different accounts or personas.

## **🔹 Advantages of Hyperpocket Auth**

- 🛡️ **Security:** Tokens and sensitive data are securely managed, reducing the risk of leaks.
- ⚡ **Simplicity:** No need to manage additional server infrastructure; the internal auth server does it all.
- 🌐 **Flexibility:** Works across different tools and agent frameworks, supporting various workflows.

• 🤝 **Compatibility:** Handles multi-account scenarios with ease, enabling more complex use cases.

Hyperpocket’s authentication flow provides the foundation for secure, scalable, and flexible tool interactions in AI-driven workflows. Let me know if you’d like further examples or clarifications! 🚀

[**Simple Auth Flow**](https://www.notion.so/Simple-Auth-Flow-17dbfa25e9fc8075b7a5e1193d8930b7?pvs=21)

[**Complex Auth Flow**](https://www.notion.so/Complex-Auth-Flow-17dbfa25e9fc8000bd04e6981bc0b4a1?pvs=21)
