import asyncio
from time import sleep
from openai import OpenAI
from hyperpocket_openai import PocketOpenAI, handle_tool_call_async
from hyperpocket.tool import function_tool
from hyperpocket.auth import AuthProvider
import requests

from prettyprint import input_user, print_agent, print_system


@function_tool(
    auth_provider=AuthProvider.REDDIT,
    scopes=["read", "identity"],
)
def get_new_reddit_posts(subreddit: str, **kwargs):
    """
    Get the newest posts from a subreddit

    Args:
        subreddit (str): The subreddit name to get the newest posts from
    """

    token = kwargs.get("REDDIT_BOT_TOKEN")
    print(token)

    URL = f"https://www.reddit.com/r/{subreddit}/new.json"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(URL, headers=headers)
    data = response.json()

    print(data)

    return data


async def simple_agent():
    p = PocketOpenAI(
        tools=[
            # from_git(
            #     "https://github.com/vessl-ai/hyperawesometools",
            #     "main",
            #     "managed-tools/slack/get-message",
            # ),
            get_new_reddit_posts,
        ]
    )

    openai_tool_specs = p.get_open_ai_tool_specs()
    llm = OpenAI()
    messages = []

    sleep(1)  ## wait for the tool to be ready

    while True:
        user_input = input_user()
        if user_input == "q":
            print_system("Good bye!")
            break
        messages.append({"role": "user", "content": user_input})

        tool_call_response = await handle_tool_call_async(
            llm=llm,
            pocket=p,
            model="gpt-4o",
            tool_specs=openai_tool_specs,
            messages=messages,
        )

        print_agent(tool_call_response)


if __name__ == "__main__":
    asyncio.run(simple_agent())
