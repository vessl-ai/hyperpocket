# Example for applying hyperpocket to OpenAI agents

This example shows how to use hyperpocket to create agents that can use multiple tools with [`openai-agents-python`](https://github.com/openai/openai-agents-python).

## Setup

```bash
uv sync
```

## Run

### 1. Set secrets in `.secrets.toml`

touch and make `.secrets.toml` file in the example directory.

### 2. Create google, slack oauth app and add credentials.

👉 To create google oauth app:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the Gmail API for your project
4. Go to "Credentials" in the left sidebar
5. Click "Create Credentials" and select "OAuth client ID"
6. Configure the OAuth consent screen if prompted
7. For application type, select "Web application"
8. Add authorized redirect URIs:

   - `http://localhost:8000/callback/google`

9. Click "Create"
10. Copy the "Client ID" and "Client Secret"
11. Add these credentials to your `.secrets.toml` file

For detailed instructions, see the official guide [here](https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid#get_your_google_api_client_id).

👉 To create slack oauth app:

1. Go to [Slack API](https://api.slack.com/apps) and click "Create New App"
2. Choose "From scratch" and give your app a name
3. Select the workspace where you want to install the app
4. Under "OAuth & Permissions", add the following scopes:

   - `chat:write`
   - `channels:read`
   - `channels:write`
   - `groups:read`
   - `im:read`
   - `mpim:read`

5. Install the app to your workspace
6. Copy the "Client ID" and "Client Secret" from "Basic Information" page
7. Add these credentials to your `.secrets.toml` file:

```toml
[auth.google]
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"

[auth.slack]
client_id = "YOUR_SLACK_CLIENT_ID"
client_secret = "YOUR_SLACK_CLIENT_SECRET"
```

### 3. Run the example

```bash
uv run openai_agents_example/main.py
```

### 4. Proceed oauth flow in the console.

The example will wait for you to complete the oauth flow in the console.

You will see the following output in the console:

```
[SLACK]
        User needs to authenticate using the following URL: https://slack.com/oauth/v2/authorize?user_scope=groups%3Ahistory%2Cchat%3Awrite%2Cim%3Ahistory%2Creactions%3Aread%2Creactions%3Awrite%2Cchannels%3Aread%2Cgroups%3Aread%2Cchannels%3Ahistory%2Cmpim%3Ahistory&client_id=YOUR_CLIENT_ID&redirect_uri=https%3A%2F%2Flocalhost%3A8001%2Fproxy%2Fauth%2Fslack%2Foauth2%2Fcallback&state=EXAMPLE_STATE
[GOOGLE]
        User needs to authenticate using the following URL: https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=https%3A%2F%2Flocalhost%3A8001%2Fproxy%2Fauth%2Fgoogle%2Foauth2%2Fcallback&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.readonly&access_type=offline&state=EXAMPLE_STATE
```

Click the link and proceed with the oauth flow.

### 5. Watch what agent does for you in the console.

- This example runs in debug mode - you can see the tool calls and responses in the console: remove the `log_level = "debug"` line in the `settings.toml`.
