# What are tools?

## **Why Do AI Agents Need Tools?**

Language models excel at processing and generating text, but they cannot independently fetch real-time data, communicate with external systems, or execute code. While they can reason and analyze information, they require external tools to interact with the digital world and take meaningful actions.

**Tools can solve this limitation.**

**With tools, AI models can extend their capabilities beyond text generation to:**

✅ Fetching live data (e.g., retrieving stock prices, weather updates)

✅ Calling APIs (e.g., sending Slack messages, querying databases)

✅ Running local code (e.g., executing Python scripts, processing WASM code)

✅ Managing files (e.g., reading and writing to disk, handling cloud storage)

## **How Tool Calling Works**

AI models with **tool-calling capabilities** can recognize when a tool is needed, select the appropriate tool, and execute it to fulfill a user’s request. Developers can design and integrate these tools, allowing AI models to take real-world actions.

**Example: AI Agent Using Tools**

- 🗣 **User:** “Can you check the latest GitHub stars for Hyperpocket?”
- 🤖 **AI Model’s Process:**
  1. Recognizes that live data is needed.
  2. Selects the appropriate tool (GitHub.GetStars).
  3. Calls the tool, fetching the latest star count from GitHub.
  4. Generates a response using the retrieved data.

## **How Hyperpocket Handles Tools**

### **Tool Categorization by Integration Method**

**Hyperpocket provides two distinct ways to integrate tools into AI agents:**

![image.png](what-are-tools/image.png)

1. **WASM Tools** : Tools executed securely in an isolated WebAssembly (WASM) environment.
2. **Function Tools** : Lightweight Python functions that can be directly integrated into workflows.

#### **1. WASM Tools**

WASM tools are executed in secure, sandboxed environments, making them ideal for scenarios requiring high security and performance isolation. These tools can either be fetched from external repositories like GitHub or loaded directly from local storage.

**WASM Tool Variants**

- **GitHub-based Execution**
  - Tools are fetched from a GitHub repository, downloaded locally, and executed via a WASM interpreter.
  - This approach is useful for managed tools maintained by Hyperpocket or open-source contributions by the community.
- **Local Execution**
  - Pre-existing tools stored locally are executed directly using their file paths.
  - Ideal for private tools or custom setups where internet access might be restricted.

**Example Command:**

```python
from hyperpocket.tool import from_git

tool = from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message")
```

#### **2. Function Tools**

Function tools are lightweight, easy-to-implement tools that utilize Python functions decorated with a specific Hyperpocket interface. These tools are ideal for quick, inline tool development or rapid prototyping.

**Example Code:**

```python
from hyperpocket.tool import function_tool

@function_tool
def get_weather(location: str) -> str:
    return f"The weather in {location} is sunny."
```

### **Tool Categorization by Availability**

Hyperpocket tools are also classified into four categories based on ownership and management, offering flexibility for various user needs.

![image.png](what-are-tools/image%201.png)

#### **🛠 Built-in Tools (provided as Function Tools)**

Built-in tools are pre-installed and included with Hyperpocket, requiring no additional setup. These tools are managed and predefined by the Hyperpocket team, allowing users to utilize them out of the box with minimal effort.

**Example Command:**

```python
from hyperpocket.tool import built_in_tool

@built_in_tool
def simple_task():
    return "This is a built-in function tool!"
```

#### **📦 Managed Tools**

Managed tools are developed by individual contributors and officially reviewed, uploaded, and maintained by the Hyperpocket team. These tools are curated for reliability and can be seamlessly integrated into workflows through the Hyperpocket framework.

**Example Command:**

```python
from hyperpocket.tool import from_git

tool = from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message")
```

#### **🌍 Community Tools (Open-Source & External Contributions)**

Community tools are open-source and shared by the broader community. These tools are managed by individual contributors through personal repositories or platforms such as LangChain-Hub, Hugging Face, and MCP. They provide diverse functionality and encourage collaboration across users.

**Example Command:**

```python
tool = from_git("https://github.com/user/custom-tool-repo", "main", "community-tools/custom-task")
```

#### ✏️ Custom Tools

Custom tools are highly personalized tools that users can directly create and deploy in their local environments. These tools are fully managed by the user or their organization and can be implemented as inline functions or packaged modules. Users can execute them using either a local Python interpreter or a secure WASM interpreter, providing maximum flexibility for bespoke workflows.

**Example Command(Inline function tool):**

```python
from hyperpocket.decorators import tool

@tool(name="custom_task", description="A custom inline function tool.")
def custom_task():
		"""
		A custom inline function tool.
		"""

    return "This is my custom tool!"
```

**Example Command (Packaged Local Tool):**

```python
from hyperpocket.tool import from_local

tool = from_local(path="./local-tools/my-tool.wasm", interpreter="wasm")
```

## Summary

### **By Integration Method**

| Integration Method     | Description                                                                                       | Catagory      |
| ---------------------- | ------------------------------------------------------------------------------------------------- | ------------- |
| Function               | Lightweight tools defined as Python functions and executed locally.                               | Function Tool |
| GitHub-based Execution | Tools fetched from GitHub repositories and executed in independent WASM runtime via interpreters. | WASM Tool     |
| Local Execution        | Tools stored locally and executed directly.                                                       | WASM Tool     |

### **By Availability**

| Tool Type       | Category       | Description                                       | Operation by                                                               |
| --------------- | -------------- | ------------------------------------------------- | -------------------------------------------------------------------------- |
| Built-in Tools  | Function       | Pre-installed tools ready for immediate use.      | Managed and predefined by Hyperpocket.                                     |
| Managed Tools   | WASM           | Community-developed tools, officially maintained. | Managed by Hyperpocket, developed by individual contributors.              |
| Community Tools | WASM, Function | Open-source tools shared by the community.        | Managed by individual contributors through GitHub or other platforms.      |
| Custom Tools    | WASM, Function | Personalized tools created and deployed by users. | Fully managed by the user, supporting inline and packaged implementations. |

**To learn how to apply our tools, please visit the pages below:**

- [Applying Local Tools](apply-local-tools.md)

- [Applying Function Tools](apply-function-tools.md)

- [Integration from GitHub](integration-from-github.md)
