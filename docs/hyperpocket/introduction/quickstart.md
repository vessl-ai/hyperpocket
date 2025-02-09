# Quick Start

This guide will help you quickly set up **Hyperpocket** with **LangChain** to build a tool-calling AI agent. In this example, **we will integrate Slack API tools that can retrieve and post messages** using Hyperpocket.

## **1️⃣ Prerequisites**

Before we begin, install the required dependencies.

**Python Version**

Python >= 3.10

**Install Required Packages**

Run the following commands to install Hyperpocket and LangChain dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
pip install hyperpocket_langchain
pip install langchain_openai
```

**Install Chromium for Playwright (if not already installed)**

Chromium is used as a runtime for WASM environment and is required to execute WASM tools. You can install and integrate chromium with playwright by:

```bash
playwright install
```

## **2️⃣ Configuration**

To use Hyperpocket, you need to create configuration files for storing credentials and API settings.

**Set Up Hyperpocket Configuration**

Create a configuration file at `<repository-root>/settings.toml` and add the following

```toml
log_level = "debug"
```

For sensitive values like Slack OAuth2 client secret, you might want to keep those values in `<repository-root>/.secrets.toml` and gitignore it.
Both files will be merged into one configuration object.

In this tutorial, you are going to use Slack App OAuth2 feature to use slack related tools. First, visit [Slack apps page](https://api.slack.com/apps/) and create new app.
If you have a proper manifest, you may use it to build the new slack app. Or you can just build the slack app from the scratch.

You'll find Client ID and Client Secret from the **Settings > Basic Information** of the app dashboard. Copy them, and paste into the `.secrets.toml` file like:

```toml
[auth.slack]
client_id = "<SLACK_CLIENT_ID>"
client_secret = "<SLACK_CLIENT_SECRET>"
```

This configuration allows Hyperpocket to authenticate with Slack.

In this tutorial, you are going to try get and post some slack messages. To do so, you have to allow the slack application to get or post one.
Visit **Features > OAuth & Permissions** of the app dashboard. In the `Scopes` section, you have to add `channels:history`, `chat:write` as bot token scopes.
Configuration is done for the app side. Now, install your app into your workspace by following [this Slack guideline](https://slack.com/help/articles/202035138-Add-apps-to-your-Slack-workspace).

## **3️⃣ Writing the Code**

Below is a breakdown of the code to set up and run the AI agent.

### **Step 1: Import Required Modules**

Import the necessary libraries for integrating Hyperpocket and LangChain.

```python
import os

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
llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
llm_with_tools = llm.bind_tools(tools)
```

### **Step 4: Define LangChain Prompt and Memory**

Create a prompt template and initialize memory to manage conversation history.

```python
# Define the conversation prompt
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a tool-calling assistant. You can help the user by calling proper tools."),
        ("placeholder", "{chat_history}"),
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

When entering a Slack-related query for the first time, the system will provide an authentication link. Follow these steps to authenticate:

- Enter a query, such as retrieving or posting a message.
- The agent will respond with an authentication link in the form of a URL. Example:
- Open the provided link in your browser and complete the authentication process.
- After authenticating, return to the interface and talk to your agent that you've done with the authentication. The agent will now be ready to perform Slack actions.

```
user(q to quit) : Get some slack messages from engr-test.

> Entering new AgentExecutor chain...

Invoking: `slack_get_messages` with `{'channel': 'engr-test', 'limit': 5}`


redirect_uri: https://localhost:8001/proxy/auth/slack/oauth2/callback
User needs to authenticate using the following URL: https://slack.com/oauth/v2/authorize?<some url parameters>

The tool execution interrupted. Please talk to me to resume.It looks like you need to authenticate in order to access the Slack messages from the "engr-test" channel. Please [click here to authenticate with Slack](https://slack.com/oauth/v2/authorize?<some url parameters>). After you've done that, let me know!

> Finished chain.
slack agent :  It looks like you need to authenticate in order to access the Slack messages from the "engr-test" channel. Please [click here to authenticate with Slack](https://slack.com/oauth/v2/authorize?<some url parameters>). After you've done that, let me know!

user(q to quit) : I'm done.

> Entering new AgentExecutor chain...

Invoking: `slack_get_messages` with `{'channel': 'engr-test', 'limit': 10}`

> Finished chain.
slack agent :  Here are some recent messages from the "engr-test" Slack channel:

1. **User Message:**
   - **User:** ASDFASDF
   - **Text:** "Hey, the HyperPocket project is awesome!"
   - **Reactions:** :+1: (123 reactions)

2. **User Message:**
   - **User:** ASDFASDF2
   - **Text:** "Hey, it's so true!"
   - **Reactions:** :+1: (456 reactions)
...
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