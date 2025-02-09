import os

from anthropic import Anthropic
from hyperpocket.tool import from_git
from hyperpocket_anthropic import PocketAnthropic


def agent():
    import asyncio

    asyncio.run(_agent())


async def _agent():
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    pocket = PocketAnthropic(
        tools=[
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/linear/get-issues",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-events",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-list",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/insert-calendar-events",
        ]
    )

    tool_specs = pocket.get_anthropic_tool_specs()

    messages = []
    while True:
        print("user(q to quit) : ", end="")
        user_input = input()
        if user_input == "q":
            break
        if user_input == "":
            continue

        messages.append({"role": "user", "content": user_input})

        while True:
            response = client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=500,
                messages=messages,
                tools=tool_specs,
            )

            messages.append({"role": "assistant", "content": response.content})

            tool_result_blocks = []
            for block in response.content:
                if block.type == "text":
                    print("[ai] response : ", block.text)

                elif block.type == "tool_use":
                    tool_result_block = await pocket.ainvoke(block)
                    tool_result_blocks.append(tool_result_block)

                    print("[tool] response : ", tool_result_block["content"])

            messages.append({"role": "user", "content": tool_result_blocks})

            if response.stop_reason != "tool_use":
                break


if __name__ == "__main__":
    agent()
