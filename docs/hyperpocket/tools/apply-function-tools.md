# Applying Function Tools

## What Are Function Tools?

Function Tools are lightweight, Python-based tools that integrate directly into AI workflows. These tools are defined
using the @tool decorator, making it simple to extend the capabilities of AI agents with minimal setup.

To explore more about Hyperpocket tools, please
visit [What are tools?](https://www.notion.so/What-are-tools-17cbfa25e9fc806c95c6d9896acfd964?pvs=21)

## **How to Use Function Tools**

Here’s an example of defining and using a Function Tool with Hyperpocket.

**Code Example: Creating and Using a Function Tool**

```python
from hyperpocket import Pocket
from hyperpocket.tool import function_tool


# Define a Function Tool
@function_tool
def get_weather(location: str) -> str:
   """Fetch the weather information for a given location."""
   return f"The weather in {location} is sunny with a high of 25°C."


# Using the Function Tool
if __name__ == "__main__":
   pocket = Pocket(tools=[get_weather])
   tool_result = pocket.invoke(tool_name="get_weather", body={"location": "Seoul"})
   print(tool_result)  # Output: The weather in Seoul is sunny with a high of 25°C.
```

## Action To do

1. **Define a Function Tool**

   Use the `@function_tool` decorator to define a Python function as a tool. Add relevant input arguments and return the desired
   output.

2. **Integrate into Your Workflow**

   Call the Function Tool directly in your Python code or integrate it with your AI agent for automated usage.

3. **Extend the Functionality**

   Combine multiple Function Tools to create more complex workflows or connect them to external APIs.

## **When to Use Function Tools?**

Use Function Tools when:

- You need lightweight, quick tasks (e.g., formatting, simple calculations, or fetching small pieces of data).
- You want tools that work natively in Python without additional setup.
- The task doesn’t require isolation or sandboxing (which is better suited for WASM Tools).
