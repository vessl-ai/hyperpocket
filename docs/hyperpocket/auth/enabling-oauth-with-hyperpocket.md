# Enabling OAuth with Hyperpocket

Hyperpocket simplifies the integration of OAuth-based authentication, making it easy to handle multi-step flows securely. OAuth is particularly useful for tools that require user authorization, such as Slack, GitHub, or Google APIs.

## **How to Apply OAuth in Hyperpocket**

1.	**Define the OAuth Configuration**

Use the OAuthHandler to set up the required credentials and endpoints.

•	**Client ID and Secret:** These are provided by the service you’re integrating with.

•	**Scopes:** Specify the permissions your tool requires.

•	**Authorization and Token URLs:** Define the endpoints for initiating OAuth and obtaining tokens.

2.	**Define the Tool**

Use the @tool decorator to create a tool with the OAuth configuration.

**Code Example: Applying OAuth**

Here’s how to define and use a Slack tool with OAuth authentication:

```python
from hyperpocket.tool import tool
from hyperpocket.auth import OAuthHandler

# Define the tool with OAuthHandler
@tool(auth=OAuthHandler(
    client_id="your_client_id",
    client_secret="your_client_secret",
    scopes=["read:messages", "write:messages"],
    auth_url="https://slack.com/oauth/authorize",
    token_url="https://slack.com/api/oauth.access"
))
def fetch_slack_messages(channel: str, limit: int = 10) -> list:
    """Fetch recent messages from a Slack channel."""
    return [{"user": "Alice", "message": "Hello!"}, {"user": "Bob", "message": "Hi!"}]

# Use the tool
if __name__ == "__main__":
    messages = fetch_slack_messages(channel="general", limit=5)
    print(messages)
```

**Why Use OAuth with Hyperpocket?**

•	**Dynamic Token Management:** Handles token issuance, storage, and refresh cycles internally.

•	**Secure Authentication:** No exposure of sensitive credentials like access tokens.

•	**Seamless Integration:** Easily integrate OAuth flows into multi-turn workflows.