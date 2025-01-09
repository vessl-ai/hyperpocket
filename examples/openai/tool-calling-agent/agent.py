from openai import OpenAI

from hyperpocket.config import secret
from hyperpocket.tool import from_git

from hyperpocket_openai import PocketOpenAI


def agent():
    import asyncio

    asyncio.run(_agent())


async def _agent():
    pocket = PocketOpenAI(
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
    tool_specs = pocket.get_open_ai_tool_specs()

    model = OpenAI(api_key=secret["OPENAI_API_KEY"])
    messages = []
    while True:
        print("user input(q to quit) : ", end="")
        user_input = input()
        if user_input == "q":
            break

        user_message = {"content": user_input, "role": "user"}
        messages.append(user_message)

        while True:
            response = model.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tool_specs,
            )
            choice = response.choices[0]
            messages.append(choice.message)
            if choice.finish_reason == "stop":
                break

            elif choice.finish_reason == "tool_calls":
                tool_calls = choice.message.tool_calls
                for tool_call in tool_calls:
                    print("[TOOL CALL] ", tool_call)
                    tool_message = await pocket.ainvoke(tool_call)
                    messages.append(tool_message)

        print("response : ", messages[-1].content)


if __name__ == "__main__":
    agent()
