from anthropic import Anthropic
from hyperpocket.config import secret
from hyperpocket.tool import from_git
from hyperpocket_anthropic import PocketAnthropic

from prettyprint import print_agent, input_user, print_system


def agent():
    import asyncio

    asyncio.run(_agent())


async def _agent():
    client = Anthropic(api_key=secret["ANTHROPIC_API_KEY"])
    p = PocketAnthropic(
        tools=[
            from_git(
                "https://github.com/vessl-ai/hyperawesometools",
                "main",
                "managed-tools/slack/get-message",
            ),
        ]
    )

    tool_specs = p.get_anthropic_tool_specs()

    messages = []
    while True:
        user_input = input_user()
        if user_input == "q":
            print_system("Good bye!")
            break
        if user_input == "":
            continue

        messages.append({"role": "user", "content": user_input})

        while True:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=messages,
                tools=tool_specs,
            )

            messages.append({"role": "assistant", "content": response.content})

            tool_result_blocks = []
            for block in response.content:
                if block.type == "text":
                    print_agent(block.text)

                elif block.type == "tool_use":
                    tool_result_block = await p.ainvoke(block)
                    tool_result_blocks.append(tool_result_block)

                    # print("[tool] response : ", tool_result_block["content"])

            messages.append({"role": "user", "content": tool_result_blocks})

            if response.stop_reason != "tool_use":
                break


if __name__ == "__main__":
    agent()
