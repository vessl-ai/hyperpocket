# LangChain

**LangChain** is a popular framework for building applications powered by language models. Hyperpocket integrates easily with LangChain, allowing you to use tools dynamically within agents.

**Example: Using Hyperpocket with LangChain**

**Code Example: Tool Calling with LangChain**

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from hyperpocket.config import secret
from hyperpocket_langchain import PocketLangchain

# Initialize Hyperpocket
pocket = PocketLangchain(
    tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message"
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message"
    ],
)

# Define LangChain components
tools = pocket.get_tools()
llm = ChatOpenAI(model="gpt-4o", api_key=secret["OPENAI_API_KEY"])
prompt = ChatPromptTemplate.from_messages([
    ("placeholder", "{chat_history}"),
    ("system", "You are a tool-calling assistant."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
agent = create_tool_calling_agent(llm, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)

# Run the agent
if __name__ == "__main__":
    while True:
        user_input = input("Enter your query (or 'q' to quit): ")
        if user_input.lower() == 'q':
            break
        response = agent_executor.invoke({"input": user_input})
        print(response["output"])
```