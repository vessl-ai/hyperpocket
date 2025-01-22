from anthropic import Anthropic
from hyperpocket.config import secret
from hyperpocket.tool import from_git
from hyperpocket_anthropic import PocketAnthropic


def agent():
    import asyncio

    asyncio.run(_agent())


async def _agent():
    client = Anthropic(api_key=secret["ANTHROPIC_API_KEY"])
    pocket = PocketAnthropic(
        tools=[
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/get-message"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/slack/post-message"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/linear/get-issues"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/google/get-calendar-events"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/google/get-calendar-list"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/google/insert-calendar-events"),
            from_git("https://github.com/vessl-ai/hyperawesometools", "main", "managed-tools/github/pr-list"),
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
