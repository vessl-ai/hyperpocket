# Anthropic

**Anthropic** provides advanced language model capabilities with its Claude models. Hyperpocket tools can be integrated for dynamic actions.

**Example: Using Anthropic with Tool Calling**

```python
from anthropic import Anthropic
from hyperpocket.tool import from_git

# Initialize Anthropic LLM
anthropic = Anthropic(api_key="YOUR_ANTHROPIC_API_KEY")

# Load a Hyperpocket tool
tool = from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message")

# Define the prompt with tool integration
prompt = f"""
You are a Slack assistant. Use the tool to fetch messages:
Tool: {tool.name}
Instructions: Fetch the last 5 messages from the 'general' channel.
"""
response = anthropic.completion(prompt=prompt)
print(response)
```