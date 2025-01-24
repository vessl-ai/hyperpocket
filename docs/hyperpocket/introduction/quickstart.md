# Quick Start

This guide will help you quickly set up **Hyperpocket** with **LangChain** to build a tool-calling AI agent. In this example, **we will integrate Slack API tools that can retrieve and post messages** using Hyperpocket.

## **1️⃣ Prerequisites**

Before we begin, install the required dependencies.

**Python Version**

python 3.10 to python 3.13 is required

**Install Required Packages**

Run the following commands to install Hyperpocket and LangChain dependencies

```bash
pip install hyperpocket_langchain
pip install langchain_openai
```

**Install Playwright (if not already installed)**

Playwright is required to run the WASM environment. Install it using

```bash
playwright install
```

## **2️⃣ Configuration**

To use Hyperpocket, you need to create configuration files for storing credentials and API settings.

**Set Up Hyperpocket Configuration**

Create a configuration file at `<repository-root>/.pocket/settings.toml` and add the following

```toml
log_level = "debug"

[git]
[git.github]
github_token = "<GITHUB_TOKEN>"

[auth.slack]
client_id = "<SLACK_CLIENT_ID>"
client_secret = "<SLACK_CLIENT_SECRET>"
```

This configuration allows Hyperpocket to fetch tools from GitHub and authenticate with Slack.

**Set Up Secret Keys**

Create a file at `<repository-root>~/.pocket/.secret.toml` and store sensitive API keys:

```toml
OPENAI_API_KEY = "<OPENAI_API_KEY>"
```

Alternatively, you can set this directly in your environment:

```toml
export OPENAI_API_KEY="<YOUR_OPENAI_API_KEY>"
```

## **3️⃣ Writing the Code**

Below is a breakdown of the code to set up and run the AI agent.

### **Step 1: Import Required Modules**

Import the necessary libraries for integrating Hyperpocket and LangChain.

```python
from hyperpocket.config import secret
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from hyperpocket_langchain import PocketLangchain
```

### **Step 2: Initialize Hyperpocket and Load Tools**

Set up Hyperpocket and fetch the tools from GitHub.

```python
# Initialize Hyperpocket and load Slack tools
pocket = PocketLangchain(
    tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
    ],
)
tools = pocket.get_tools()
```

### **Step 3: Initialize OpenAI LLM**

Configure the OpenAI language model (LLM) for use with LangChain.

```python
# Initialize OpenAI LLM
llm = ChatOpenAI(model="gpt-4o", api_key=secret["OPENAI_API_KEY"])
llm_with_tools = llm.bind_tools(tools)
```

### **Step 4: Define LangChain Prompt and Memory**

Create a prompt template and initialize memory to manage conversation history.

```python
# Define the conversation prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("placeholder", "{chat_history}"),
        ("system", "You are a tool-calling assistant. You can help the user by calling proper tools."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Initialize memory for conversation history
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
```

### **Step 5: Create the LangChain Agent**

Combine the tools, LLM, prompt, and memory to create a LangChain agent.

```python
# Create LangChain agent
agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
)
```

### **Step 6: Run the Agent (Interactive Mode)**

Run the agent interactively in a terminal or Jupyter Notebook to test its functionality.

```python
print("Hello, This is a simple Slack agent using Hyperpocket.")

while True:
    user_input = input("user (q to quit): ")
    
    if user_input.lower() == "q":
        print("Goodbye!")
        break
    
    response = agent_executor.invoke({"input": user_input})
    print("agent:", response["output"])
    print()
```

### **Step 7: Test the Agent with a Single Query**

For a simpler test, try running a single query.

```python
# Test the agent with a single input
test_input = "Retrieve the last message from #general"
response = agent_executor.invoke({"input": test_input})

print("User Input:", test_input)
print("Agent Response:", response["output"])
```

## **4️⃣ Run the Script**

Once everything is set up, execute the script:

```
python langchain_example.py
```

**Expected Output**

```
Hello, This is a simple Slack agent using Hyperpocket.
user (q to quit) :
```

## **5️⃣ Example Usage**

### Step 1 : Set Up Slack API Permissions

Before using Slack-related functionalities, make sure your Slack app has the proper permissions to post and retrieve messages from channels. Follow these steps:

1.	Go to the [Slack API Dashboard](https://api.slack.com/).

2.	Navigate to **Your Apps** and select your app.

3.	Under the **OAuth & Permissions** section, ensure your app has the following scopes:

- channels:history (for retrieving messages)
- channels:write (for posting messages)

4.	Save your changes and reinstall the app to apply the updated permissions.

### Step2 : Authenticate via Slack

When entering a Slack-related query for the first time, the system will provide an authentication link. Follow these steps to authenticate:

1. Enter a query, such as retrieving or posting a message.
2. The agent will respond with an **authentication link** in the form of a URL. Example:

```bash
INFO:     127.0.0.1:51151 - "GET /auth/slack/oauth2/callback?code=****&state=**** HTTP/1.1" 200 OK
```

1. Open the provided link in your browser and complete the authentication process.
2. After authenticating, return to the interface and enter **any message** to confirm the setup. The agent will now be ready to perform Slack actions.

### **Example Commands**

**Retrieve the Last Message from Slack Channel**

```python
user (q to quit) : Retrieve the last message from #general
agent : "Please authenticate using this link: [Slack Authentication Link]"
INFO:     127.0.0.1:51151 - "GET /auth/slack/oauth2/callback?code=****&state=**** HTTP/1.1" 200 OK
user (q to quit) : Okay
agent : "The last message in #general is: 'Hello, world!'"
```

**Post a message to Slack**

```bash
user (q to quit) : Post 'Good morning' to #random
agent : "Please authenticate using this link: [Slack Authentication Link]"
INFO:     127.0.0.1:51149 - "GET /auth/slack/oauth2/callback?code=****&state=**** HTTP/1.1" 200 OK
user (q to quit) : Okay
agent : "Message successfully posted to #random"
```

## Full code

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from hyperpocket.config import secret
from hyperpocket_langchain import PocketLangchain

if __name__ == '__main__':
    pocket = PocketLangchain(
        tools=[
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
        ],
    )
    tools = pocket.get_tools()
    llm = ChatOpenAI(model="gpt-4o", api_key=secret["OPENAI_API_KEY"])
    prompt = ChatPromptTemplate.from_messages(
        [
            ("placeholder", "{chat_history}"),
            (
                "system",
                "You are a tool calling assistant. You can help the user by calling proper tools",
            ),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
    )

    print("Hello, This is simple slack agent using hyperpocket.")
    while True:
        print("user(q to quit) : ", end="")
        user_input = input()

        if user_input is None or user_input == "":
            continue
        elif user_input == "q":
            print("Good bye!")
            break

        response = agent_executor.invoke({"input": user_input})
        print("agent : ", response["output"])
        print()
```