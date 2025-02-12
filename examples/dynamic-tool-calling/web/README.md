# Dynamic tool calling demo web



### install vite, uv 
```shell
brew install vite
brew install uv
```

### sync uv
```shell
cd backend
uv sync
```

### create `.secret.toml`
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
```shell
uv run ./start.sh
```

### run frontend
```shell
cd ../frontend
vite
```