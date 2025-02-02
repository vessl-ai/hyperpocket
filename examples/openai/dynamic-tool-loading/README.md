# Dynamic Tool Loading Demo

This example is a demo about dynamic tool loading.

## User scenario

1. a user write their own code in `tool register` tab
2. the written code is uploaded to github
    - optionally the user can set auth or dependencies.
3. the tool is dynamically registered from the uploaded github url. after that, the user can check their registered tool
   in `Tool list` section of the `chatbot` tab
4. the user ask the chatbot to call their registered tool.

## Prerequisite

1. Install `node`(for javascript), `uv`(for python) to bundling packages.

```shell
brew install uv
brew install node
```

2. Sync dependencies

```shell
uv sync
```

3. Set auth app client_id and client_secret in `.secrets.toml`

```toml
[auth.github]
client_id = ""
client_secret = ""

[auth.slack]
client_id = ""
client_secret = ""

[auth.google]
client_id = ""
client_secret = ""
```

4. Set `openai_api_key` and `github_token` in environment variables or python-dotenv

```shell
export OPENAI_API_KEY=""
export GITHUB_TOKEN=""
```

or write this in `.env`

```text
GITHUB_TOKEN=""
OPENAI_API_KEY=""
```

5. Run `main.py`

```shell
uv run python main.py
```
