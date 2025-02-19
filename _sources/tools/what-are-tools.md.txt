# What are tools?

## Why do AI Agents need tools?

Language models excel at processing and generating text, but they cannot independently fetch real-time data, communicate with external systems, or execute code. While they can reason and analyze information, they require external tools to interact with the digital world and take meaningful actions. Tools can solve this limitation.

With tools, AI models can extend their capabilities beyond text generation to:

- Fetching live data (e.g., retrieving stock prices, weather updates)
- Calling APIs (e.g., sending Slack messages, querying databases)
- Running local code (e.g., executing Python scripts, processing WASM code)
- Managing files (e.g., reading and writing to disk, handling cloud storage)

## How tool calling works

AI models with **tool-calling capabilities** can recognize when a tool is needed, select the appropriate tool, and execute it to fulfill a user’s request. Developers can design and integrate these tools, allowing AI models to take real-world actions.

- 🗣 **User:** “Can you check the latest issue for vessl-ai/hyperpocket?”
- 🤖 **AI Model’s Process:**
  1. Recognizes that live data is needed.
  2. Selects the appropriate tool (GitHub.GetIssue).
  3. Calls the tool, fetching the latest issue from GitHub.
  4. Generates a response using the retrieved data.

## How Hyperpocket handles tools

### Tool categorization by integration method

Hyperpocket provides two ways to integrate tools into AI agents:

1. **Function Tools** : Lightweight Python functions that can be directly integrated into workflows.
2. **Sandboxed Tools** : Tools executed securely in an isolated environment.

#### Function Tools

Function Tools are lightweight, easy-to-implement tools that utilize Python functions decorated with a specific Hyperpocket interface. These tools are ideal for quick, inline tool development or rapid prototyping. To make Function Tool, the original function must have a docstring or implement `__doc__`.

```python
from hyperpocket.tool import function_tool

@function_tool
def get_weather(location: str) -> str:
    """
    Get the weather in a specific location.

    Args:
        location (str): The location to get the weather for.

    Returns:
        str: The weather in the specified location.
    """
    return f"The weather in {location} is sunny."
```

#### Sandboxed Tools

Sandboxed tools are executed in secure, sandboxed environments, making them ideal for scenarios requiring high security and performance isolation.
Those environment can be one of containerized environment, WASM runtime environment, or anything else.
These tools can either be fetched from external repositories like GitHub or loaded directly from local storage.

Sandboxed Tool has two following variants:

**Git-based Execution**

- Tools are fetched from a Git repository, downloaded locally, and executed on top of an isolated environment such as containers.
- This approach is useful for sharing tools over open-source contributions by the community.

**Local Execution**

- Pre-existing tools stored locally are executed directly using their file paths.
- Ideal for testing your tools currently you are building.

Below is an example code that integrates sandboxed tools. For more detail, find more on [Using Sandboxed Tools](https://vessl-ai.github.io/hyperpocket/tools/using-sandboxed-tools.html)

```python
from hyperpocket_langchain import PocketLangchain

pocket = PocketLangchain(
    tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
        "/Users/possum/tools/slack/get-messages",
    ]
)
```


### Tool categorization by availability

#### Built-in Tools

Built-in tools are pre-installed and included in Hyperpocket to manage authentication sessions.

#### Public Tools (open-source)

Public tools are open-source and shared by the broader community, including individual contributors, other open-source projects, and Hyperpocket team as well. These tools can be hosted on various platforms such as Hyperpocket repository, other GitHub repositories.

#### Your own tools

Custom tools are highly personalized tools that users can directly create and deploy in their local environments. These tools are fully managed by the user or their organization and can be implemented as inline functions or packaged modules. Users can execute them using either a local Python interpreter or a secure WASM interpreter, providing maximum flexibility for bespoke workflows.
