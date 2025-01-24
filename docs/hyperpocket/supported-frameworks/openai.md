# OpenAI

**OpenAI** is a widely used platform for language models like GPT-4. With Hyperpocket, you can extend OpenAI’s capabilities by integrating tools directly.

**Example: Using Hyperpocket with OpenAI**

```python
from openai import ChatCompletion
from hyperpocket.tool import from_git

# Load a tool
tool = from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message")

# Define the OpenAI prompt
prompt = f"""
You are an assistant. Use the tool below to post a message:
Tool: {tool.name}
Instructions: Post "Hello, team!" to the 'general' channel.
"""
response = ChatCompletion.create(model="gpt-4", messages=[{"role": "system", "content": prompt}])
print(response["choices"][0]["message"]["content"])
```