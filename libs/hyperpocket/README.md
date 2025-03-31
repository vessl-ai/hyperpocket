<p align="center">
<img src="logo.png" alt="hyperpocket" width="570"/>
</p>

# Hyperpocket 👛

Hyperpocket is where tools belong. Power your agent up with a pocket of tools. 👛

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

setting hyperpocket config in your current working directory

`${WORKDIR}/.secret.toml`

```toml
[auth.slack]
client_id = "<SLACK_CLIENT_ID>"
client_secret = "<SLACK_CLIENT_SECRET>"
```

setting openai api key env for this example.

```shell
export OPENAI_API_KEY=<OPENAI_API_KEY>
```

### 3. Writing code

`langchain_example.py`

```python
import os

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from hyperpocket_langchain import PocketLangchain

if __name__ == '__main__':
    pocket = PocketLangchain(
        tools=[
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
        ],
    )
    tools = pocket.get_tools()
    llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
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

from langchain_openai import ChatOpenAI

from hyperpocket_langchain import PocketLangchain

pklc = PocketLangchain(
    tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
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

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import tools_condition

from hyperpocket_langgraph import PocketLanggraph

pklg = PocketLanggraph(
    tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
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
import os

from llama_index.core.agent import FunctionCallingAgent
from llama_index.llms.openai import OpenAI

from hyperpocket_llamaindex import PocketLlamaindex

llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pocket = PocketLlamaindex(
    tools=[
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/linear/get-issues",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-events",
        "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-list",
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

Running `hyperpocket config init` will create your config file in `${WORKDIR}/settings.toml` and
`${WORKDIR}/.secrets.toml`

The `settings.toml` looks as follows.

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

[auth.slack] # add your slack app's client id and secret for slack auth
client_id = "" # your slack client id
client_secret = "" # your slack client secret
```

Or you put some sensitive data on `{WORKDIR}/.secrets.toml`

```toml
[auth.slack] # add your slack app's client id and secret for slack auth
client_id = "" # your slack client id
client_secret = "" # your slack client secret
```

- in this case, by putting your slack app client_id and client_secret on `.secrets.toml`, you can manage your sensitive
  data more safely.

#### When using Basic Auth

IMPORTANT: You should update `auth_encryption_secret_key` in `{WORKDIR}/.secret.toml` with your own secret key.

```toml
[auth]
auth_encryption_secret_key = "<YOUR_SECRET_KEY>"
```

The secret key should be a 32 Base64 encoded string.

You can generate the secret key with the following command.

```shell
pip install cryptography
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

#### How to integrate github OAuth app

1. Follow the github documentation to create a new OAuth
   app. https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app

- While creating your github OAuth app, configuring your app's `Authorization callback URL` is different for your
  development environment and production environment.
  - For local testing environment, you can use `https://localhost:8001/proxy/auth/<provider>/callback` for TLS enabled
    redirect url. (ex. `https://localhost:8001/proxy/auth/github/callback`)
    - **Note**: Default port for hyperpocket dev server is `8000`. If you are using a different port, make sure to
      replace `8000` with your actual port number.
    - **Note**: But for easy dev experience, you can use TLS proxy on port `8001` provided out-of-the-box.
      - You can change the `proxy` prefix in settings.toml to your desired prefix with
        `callback_url_rewrite_prefix` key.
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

#### How to start adding a new token auth

1. Generate boilerplate codes for token-based auth services ?

```
# service_name should be lowercase including underscore
poetry run hyperpocket devtool create-token-auth-template {service_name}
```

It will generate boilerplate code lines for a new token-based auth service

2. Extend AuthProvider enum to add your new auth provider.

```python
class AuthProvider(Enum):
SERVICE = 'service'
```

3. Specify auth provider for tools

1) github repo or local

```toml
[auth]
auth_provider = "{service_name}"
auth_handler = "{service_name}-token"
scopes = []
```

2. function_tool

```python
@function_tool(
    auth_provider=AuthProvider.SERVICE
)
def my_function(**kwargs):
```

#### How to Start Developing a New Tool

1. Generate Boilerplate Template for the Tool

```bash
# tool_name must be lowercase and can include underscores
poetry run hyperpocket devtool create-tool-template your_own_tool
```

This command will generate the boilerplate directory and files for a new tool.

2. Configure the `config.toml`

Define the language, `auth_provider`, scopes, and other required settings in the `config.toml` file.

```toml
# Example configuration
name = "google_delete_calendar_events"
description = "Delete Google Calendar events"
language = "python"

[auth]
auth_provider = "google"
scopes = ["https://www.googleapis.com/auth/calendar"]
```

3. Develop the Tool Logic

Implement the `request_model` and the necessary functions for your tool's logic in the `__main__.py` file.

4. Build Your Tool

Use the Hyperpocket CLI to build your tool.

```bash
# Specify the tool_path or run the command inside the tool's directory
poetry run hyperpocket devtool build-tool ./your-own-tool
```
