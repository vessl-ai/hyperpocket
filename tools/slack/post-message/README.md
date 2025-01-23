# slack-post-message
This is a simple script to post a message to a slack channel using the slack API.
This script takes channel, message as input and posts the message to the slack channel.
This script will output if the message is posted successfully or not.

## Input
The input json file should have the following format:
```
{
  "channel": "channel_name",
  "text": "message_to_post"
}
```
The input json will be passed via standard input.

## Output
The output will be a string indicating if the message is posted successfully or not.

## Authentication
The script uses the slack API to post the message. The slack API requires an authentication token to post the message.
The authentication token should be passed as an environment variable `SLACK_BOT_TOKEN`.

## Usage
```shell
$ cat input
{
  "channel": "#engineering",
  "text": "Hello World!"
}
$ export SLACK_BOT_TOKEN="<slack_bot_token>"
$ cat input | python slack_post_message.py
```
