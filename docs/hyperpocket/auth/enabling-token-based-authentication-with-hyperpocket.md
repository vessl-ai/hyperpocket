# Enabling Token-Based Authentication with Hyperpocket

Hyperpocket support token based authentication that is used in case user already have their own token, or you can't choose OAuth flow.

This approach is simple and efficient, making it perfect for lightweight workflows.

## How to Apply Token Authentication

### 1. Define the Token Configuration

Pass the token or API key as part of the auth parameter in the @tool decorator.

### 2. Define the Tool

Use the @tool decorator to create a tool with token-based authentication.

#### Code Example: Applying Token Authentication

Here’s how to define and use a tool with an API key:

```python
from slack_sdk import WebClient

from hyperpocket.auth import AuthProvider
from hyperpocket.tool import function_tool


@function_tool(
    auth_provider=AuthProvider.SLACK,
    auth_handler="slack-token",
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

## Why Do We Use Token-Based Authentication with Hyperpocket?

- **Quick Setup:** Requires minimal configuration.
- **Lightweight Workflow:** Ideal for single-step operations with static credentials.
- **Secure Credential Management:** Tokens are securely passed and managed within Hyperpocket’s internal environment.
