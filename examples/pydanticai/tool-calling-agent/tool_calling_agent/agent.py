import asyncio

from hyperpocket_pydanticai import PocketPydanticAI
from pydantic_ai import Agent


async def run_agent(pocket: PocketPydanticAI):
    tools = pocket.get_tools()
    agent = Agent(
        "openai:gpt-4o",
        system_prompt="You are a tool calling assistant. You can help the user by calling proper tools",
        tools=tools,
    )

    print("\n\n\n")
    print("Hello, this is pydantic_ai agent.")

    history = []
    while True:
        print("user(q to quit) : ", end="")
        user_input = input()
        if user_input == "q":
            print("Good bye!")
            break
        if user_input.strip() == "":
            continue

        print("agent : ", end="")
        async with agent.run_stream(user_input, message_history=history) as result:
            async for message in result.stream_text(delta=True):
                print(message, end="")

            history = result.all_messages()

        # new line
        print()


if __name__ == "__main__":
    with PocketPydanticAI(
        tools=[
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/linear/get-issues",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-events",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-list",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/insert-calendar-events",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/list-pull-requests",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/read-pull-request",
        ],
    ) as pocket:
        asyncio.run(run_agent(pocket))
