import asyncio
from time import sleep
from openai import OpenAI
from hyperpocket_openai import PocketOpenAI, handle_tool_call_async
from hyperpocket.tool import from_git

from prettyprint import input_user, print_agent, print_system


async def simple_agent():
    p = PocketOpenAI(
        tools=[
            from_git(
                "https://github.com/vessl-ai/hyperawesometools",
                "main",
                "managed-tools/slack/get-message",
            ),
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
