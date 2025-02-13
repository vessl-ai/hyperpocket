# Dynamic tool calling demo web



### install vite, uv 
```shell
brew install vite, tsc
brew install uv
```

### setting backend
    
in web/backend
```shell
uv sync
uv run playwright install
```

### setting frontend

in web/frontend
```shell
npm install
```

### create `.secrets.toml` in `web/backend/`

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


### set openai api key
```shell
export OPENAI_API_KEY=<YOUR_KEY>
```

or write the key on `.env` file
```text
OPENAI_API_KEY=<YOUR_KEY>
```

### run backend

in web/backend
```shell
uv run ./start.sh
```

### run frontend

in web/frontend
```shell
vite
```
