# Getting Started

getting started langchain tool-calling-agent example with hyperpocket

### 1. Prerequisite

install hyperpocket package

```shell
pip install hyperpocket_langchain
pip install langchain_openai
```

install playwright

```shell
playwright install
```

### 2. Configuration

setting hyperpocket config in `~/.pocket/`

`~/.pocket/settings.toml`

```toml
log_level = "debug"

[git]
[git.github]
github_token = "<GITHUB_TOKEN>"

[auth.slack]
client_id = "<SLACK_CLIENT_ID>"
client_secret = "<SLACK_CLIENT_SECRET>"
```

`~/.pocket/.secret.toml`

```toml
OPENAI_API_KEY = "<OPENAI_API_KEY>"
```

- or just set this in your env

### 3. Writing code

`langchain_example.py`

```python
from hyperpocket.config import secret
from hyperpocket.tool import from_git
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from hyperpocket_langchain import PocketLangchain

if __name__ == '__main__':
    pocket = PocketLangchain(
        tools=[
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
        ],
    )
    tools = pocket.get_tools()
    llm = ChatOpenAI(model="gpt-4o", api_key=secret["OPENAI_API_KEY"])
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a tool calling assistant. You can help the user by calling proper tools",
            ),
            ("placeholder", "{chat_history}"),
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

### 4. Done !

```shell
python langchain_example.py
```
