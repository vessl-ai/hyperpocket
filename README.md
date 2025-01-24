# Hyperpocket 👛

Hyperpocket is where tools belong. Power your agent up with a pocket of tools. 👛

<figure>
<img src="logo.png" alt="hyperpocket" width="200"/>
</figure>

## Introduction

Hyperpocket is a tool that allows you to easily use tool and auth for agents on your machine.

**_Start fast._** Just install Hyperpocket and use it. We know you don't have time to authenticate to our server.

**_Go securely._** Not like others, you are the only one who knows your secret tokens. We do NOT. All of your secret
tokens belong to your infrastructure, not ours.

**_Power up with public tools._** Without worries for tool integration, use others' tools just with copy-and-paste the
link to the tool. Your tool will run on isolated environment based on WebAssembly technology, and you don't have to deal
with the dependency spaghetti.

**_Battery Included_** You can use popular tools and authentication providers out-of-the-box.

## Getting Started

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

### 4. Done !

```shell
python langchain_example.py
```

## Usage

Supported agent frameworks

- [x] Langgraph [link](https://www.langchain.com/langgraph)
- [x] Langchain [link](https://www.langchain.com/)
- [x] Llamaindex [link](https://www.llamaindex.ai/)

Or just use LLM API Clients out of the box.

- [x] OpenAI [link](https://openai.com/)
- [x] Anthropic [link](https://www.anthropic.com/)

### Using out-of-the-box tools

```python
from hyperpocket.tool import from_git
from langchain_openai import ChatOpenAI

from hyperpocket_langchain import PocketLangchain

pklc = PocketLangchain(
    tools=[
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
    ]
)
tools = pklc.get_tools()

llm = ChatOpenAI()
llm_tool_binding = llm.bind_tools(tools)
llm_tool_binding.invoke(...)
```

### Using out-of-the-box auth for various tools

There are two kinds of auth process, one is using system auth(developer api key) and the other is using end user auth.

Pocket provides way to use end user auth easily.
(Of course, you can also just set your STRIPE_API_KEY when using Stripe API related tools)

- Supported methods

  - [x] OAuth
  - [x] Token
  - [ ] Basic Auth (Username, Password)

- Supported OAuth Providers

  - [x] Google
  - [x] GitHub
  - [x] Slack
  - [x] Reddit
  - [x] Calendly
  - [ ] Facebook
  - [ ] X (Previously Twitter)
  - [ ] LinkedIn
  - [ ] Discord
  - [ ] Zoom
  - [ ] Microsoft
  - [ ] Spotify
  - [ ] Twitch

- Supported Token Providers
  - [x] Notion
  - [x] Slack
  - [x] Linear
  - [x] Gumloop
  - [x] Github

You can manage your auths in request-wise level. (e.g. you can use different auths for different requests)

```python
from hyperpocket.tool import from_git
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import tools_condition

from hyperpocket_langgraph import PocketLanggraph

pklg = PocketLanggraph(
    tools=[
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
    ],
)
llm = ChatOpenAI()

# Langgraph
pk_tool_node = pklg.get_tool_node()
llm_tool_binding = llm.bind_tools(pklg.get_tools())

# ...

graph_builder = StateGraph(MessagesState)

graph_builder.add_node('llm', llm)
graph_builder.add_node('tools', pk_tool_node)
graph_builder.add_edge(START, llm)
graph_builder.add_conditional_edges("llm", tools_condition)
graph_builder.add_edge(pk_tool_node, llm)

# ...

graph_builder.compile()

```

```python
from hyperpocket.config import secret
from hyperpocket.tool import from_git
from llama_index.core.agent import FunctionCallingAgent
from llama_index.llms.openai import OpenAI

from hyperpocket_llamaindex import PocketLlamaindex

llm = OpenAI(api_key=secret["OPENAI_API_KEY"])
pocket = PocketLlamaindex(
    tools=[
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/linear/get-issues"),
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/google/get-calendar-events"),
        from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/google/get-calendar-list"),
    ]
)
tools = pocket.get_tools()

agent = FunctionCallingAgent.from_tools(tools=tools, llm=llm)
```

### Auth flow included

```text
Human: List my slack messages in 'general' channel

Assistance: It looks like you need to authenticate to access the Slack messages. Please use [this link](https://slack.com/oauth/v2/authorize?user_scope=SCOPES&client_id=CLIENT_ID&redirect_uri=REDIRECT_URL) to authenticate your Slack account, and then let me know when you're done!

Human: done.

Assistance: Here are the recent 10 messages.
(...)


```

### Config

Running `hyperpocket config init` will create your config file in `$HOME/.pocket/settings.toml`

The `settings.toml` looks as follows.

TODO: Add `secrets.toml`.

```toml
log_level = "debug"
internal_server_port = "8000" # optional, default is 8000
public_hostname = "localhost" # optional, default is localhost
public_server_protocol = "https" # optional, default is https
public_server_port = "8001" # optional, default is 8001
enable_local_callback_proxy = "true" # optional, default is true, can be turned off when running in production behind TLS termination
callback_url_rewrite_prefix = "proxy" # optional, default is proxy, auth callback url prefix

[session]
session_type = "redis" # optional, default is in-memory
[session.redis]
host = "localhost"
port = 6379
db = 0

[git]
[git.github]
github_token = "<Your github PAT>" # optional, your github personal access token
app_id = "<Your github app id>" # optional, your github app id
app_installation_id = "<Your github app installation id>" # optional, your github app installation id
app_private_key = "<Your github app private key>" # optional, your github app private key

[auth]
[auth.slack] # add your slack app's client id and secret for slack auth
client_id = "" # your slack client id
client_secret = "" # your slack client secret

[auth.github] # add your github app's client id and secret for github auth
client_id = "" # your github client id
client_secret = ""  # your github client secret
```

#### How to integrate github OAuth app

1. Follow the github documentation to create a new OAuth
   app. https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app

- While creating your github OAuth app, configuring your app's `Authorization callback URL` is different for your
  development environment and production environment.
  - For local testing environment, you can use `https://localhost:8001/auth/<provider>/callback` for TSL enabled redirect url. (ex. `https://localhost:8001/auth/github/callback`)
    - **Note**: Default port for hyperpocket dev server is `8000`. If you are using a different port, make sure to
      replace `8000` with your actual port number.
  - For production environment, you can use `https://yourdomain.com/auth/github/callback`
    - **Note**: Make sure to replace `yourdomain.com` with your actual domain name that this app will be hosted on.

#### How to integrate SLACK OAuth app

1. Follow the slack documentation to create a new Oauth APP. https://api.slack.com/quickstart

2. Setting Redirect URLs, Scopes at OAuth & Permissions tap in slack APP page

- Redirect URLs :
  `{public_server_protocol}://{public_hostname}:[{public_server_port}]/{callback_url_rewrite_prefix}/auth/slack/oauth2/callback`
- Scopes : What you want to request to user.
  - Recommended scopes :
    - channels:history,
    - channels:read,
    - chat:write,
    - groups:history,
    - groups:read,
    - im:history,
    - mpim:history,
    - reactions:read,
    - reactions:write,

3. Set your Slack APP Client ID / Client Secret in `$HOME/.pocket/settings.toml`
