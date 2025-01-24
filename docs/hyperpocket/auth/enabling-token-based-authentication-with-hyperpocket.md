# Enabling Token-Based Authentication with Hyperpocket

Token-based authentication in Hyperpocket is ideal for tools that rely on pre-configured static credentials, such as API keys or bearer tokens. This approach is simple and efficient, making it perfect for lightweight workflows.

## **How to Apply Token Authentication**

1.	**Define the Token Configuration**

Pass the token or API key as part of the auth parameter in the @tool decorator.

2.	**Define the Tool**

Use the @tool decorator to create a tool with token-based authentication.

**Code Example: Applying Token Authentication**

Here’s how to define and use a tool with an API key:

```python
from hyperpocket.tool import tool

# Define the tool with token-based authentication
@tool(auth={"api_key": "YOUR_API_KEY"})
def get_weather(location: str) -> str:
    """Fetch the weather for a given location."""
    return f"The weather in {location} is sunny with a high of 25°C."

# Use the tool
if __name__ == "__main__":
    location = "Seoul"
    weather = get_weather(location)
    print(weather)  # Output: The weather in Seoul is sunny with a high of 25°C.
```

## **Why Use Token-Based Authentication with Hyperpocket?**

•	**Quick Setup:** Requires minimal configuration.

•	**Lightweight Workflow:** Ideal for single-step operations with static credentials.

•	**Secure Credential Management:** Tokens are securely passed and managed within Hyperpocket’s internal environment.