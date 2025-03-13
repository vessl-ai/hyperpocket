import os

from openai import OpenAI
from hyperpocket_openai import PocketOpenAI


def agent():
    import asyncio

    asyncio.run(_agent())


async def _agent():
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    with PocketOpenAI(
        client=client,
        tools=[]
    ) as pocket:
        tool_specs = pocket.get_open_ai_tool_specs()
        messages = [
            {
                "role": "system",
                "content": """
    You are a helpful assistant that can use the available tools to help the user.
    Especially have two abilities regarding the tool invocation:
    1. By invoking tool `find_tool`: You can search the web to find the name of the proper tool that can meet the user's request, along with the JSON schema of the tool arguments.
    2. By invoking tool `invoke_tool`: You can invoke the found tool by providing the tool name and the tool arguments.

    Help the user and invoke the tool if necessary.
    """,
            },
        ]
        while True:
            print("user input(q to quit) : ", end="")
            user_input = input()
            if user_input == "q":
                break

            user_message = {"content": user_input, "role": "user"}
            messages.append(user_message)

            while True:
                response = client.chat.completions.create(
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
