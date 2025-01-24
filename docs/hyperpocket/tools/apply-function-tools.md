# Using Function Tools

## What Are Function Tools?

Function Tools are lightweight, Python-based tools that integrate directly into AI workflows. These tools are defined
using the `@function_tool` decorator, making it simple to extend the capabilities of AI agents with minimal setup.

You can also easily add supported auth methods. Details are below. 

## Example

Code Example: Creating and Using a Function Tool with Langchain and OpenAI

```python
from hyperpocket.tool import function_tool
from hyperpocket_langchain import PocketLangchain

from langchain.agents import 
from langchain_openai import ChatOpenAI

# Define a Function Tool
@function_tool
def get_weather(location: str) -> str:
   """Fetch the weather information for a given location."""
   return f"The weather in {location} is sunny with a high of 25°C."


# Using the Function Tool
if __name__ == "__main__":
   pocket = PocketLangchain(tools=[get_weather])

   tools = pocket.get_tools()
   llm = ChatOpenAI(model="gpt-4o")
   prompt = ChatPromptTemplate.from_message(
      # ...
   )
   agent = create_tool_calling_agent(llm, tools, prompt)
   agent_executor = AgentExecutor(agent=agent, tools=tools)
   user_input = # user input
   response = agent_executor.invoke(user_input)
   print(response)
   
```

## Guides

### Using `@function_tool` decortator

1. Define a Function Tool

   Use the `@function_tool` decorator to define a Python function as a tool. Add relevant input arguments and return the desired
   output.

2. (Optional) Add auth capability for end user. 

   You can simply add predefined auth methods by specifing auth providers in the decorator.

   Example:
   ```python
   from hyperpocket.auth import AuthProvider
   @function_tool(
      auth_provider=AuthProvider.SLACK
   )
   def some_slack_action():
      ...
   ```
   This example shows `some_slack_action` function will use Slack auth methods(OAuth or tokens) provided by Hyperpocket.
   
   See [Auth](https://vessl-ai.github.io/hyperpocket/auth/index.html) for more details.
   

3. Initialize pocket and plug into your LLMs.
  
   Initialize a pocket instance and put your tool inside.
   
   For example for Langchain,
   ```python
   from hyperpocket_langchain import PocketLangchain 

   pocket = PocketOpenAI(
      tools=[
         some_slack_action,
      ]
   )
   ```

   Generate tool specs and plug them into your LLM client or workflow.
   For example for Langchain with OpenAI as LLM engine,
   ```python
   # (import langchain related here)
   
   tools = pocket.get_tools()
   llm = ChatOpenAI(model="gpt-4o")

   ...
   # Define prompts
   prompts = ChatPromptTemplate.from_messages([
      ... # prompt and messages
   ])

   # using agent executor
   memory = ConversationBufferMemory(...)
   agent = create_tool_calling_agent(llm, tools, prompt)
   agent_executor = AgentExecutor(agent=agent,tools=tools,memory=memory)

   # invoke
   user_input = ... # get user input
   agent_executor.invoke(user_input)
   ```

### (Advanced) Postprocessing the tool call results

There are situations that the data your tool returns needed to be modified - like when the response exceeds LLM's context window.

Hyperpocket provides advanced usages that you can postprocess the tool call results, with not changing the tool code itself.

See [TBD](ff) for details.

