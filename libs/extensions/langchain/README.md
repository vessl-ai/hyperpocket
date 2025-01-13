## Langchain extensions

### Biding Pocket Tools

```python
from hyperpocket.config.settings import settings
from hyperpocket.tool import from_git
from langchain_openai import ChatOpenAI

from hyperpocket_langchain import PocketLangchain

pocket = PocketLangchain(tools=[
    from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
    from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
])
# get langchain compatible tools from pocket
tools = pocket.get_tools()

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=settings["OPENAI_API_KEY"]
)

# bind tool with llm
llm_with_tools = llm.bind_tools(tools)
```

### Agent Examples

```python


from hyperpocket.tool import from_git
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from hyperpocket_langchain import PocketLangchain

pocket = PocketLangchain(tools=[
    from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
    from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
])

# get langchain compatible tools from pocket
tools = pocket.get_tools()

llm = ChatOpenAI()

prompt = ChatPromptTemplate.from_messages(
    [
        ("placeholder", "{chat_history}"),
        (
            "system",
            "You are very powerful linear assistant. You can help the user do something like commenting, get some issues",
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
    handle_parsing_errors=True
)
```
