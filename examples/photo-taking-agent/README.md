# Photo-taking Agent Demo

This example is a demo about taking a photo by using compute tool with agent.

## User scenario

1. users request to take a photo.
2. the agent takes a picture by using compute tool.
3. users can request to transform their photos into sticker photos.
4. the agent transforms user's photo into sticker photos by calling diffusion model.
5. once users get their desired sticker photos, they can request to get their photos via email.

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

3. Set auth app client_id and client_secret in `.secrets.toml`(optional)

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

5. Set `PHOTO_BOOTH_PICTURE_PATH` and `DIFFUSION_MODEL_URL` in environment variables or python-dotenv

```shell
export PHOTO_BOOTH_PICTURE_PATH=""
export DIFFUSION_MODEL_URL=""
```

```text
PHOTO_BOOTH_PICTURE_PATH=""
DIFFUSION_MODEL_URL=""
```

6. Run `main.py`

```shell
uv run python main.py
```