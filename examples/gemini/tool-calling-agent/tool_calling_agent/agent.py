import os

from google import genai
from google.genai import types

from hyperpocket_gemini import PocketGemini

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def agent():
    import asyncio

    asyncio.run(_agent())


async def _agent():
    pocket = PocketGemini(
        tools=[
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-message",
        ]
    )

    tool_specs = pocket.get_gemini_tool_specs()

    client = genai.Client(
        api_key=GEMINI_API_KEY,
    )
    messages = []
    while True:
        print("user input(q to quit) : ", end="")
        user_input = input()
        if user_input == "q":
            break

        user_prompt_content = types.Content(
            role='user',
            parts=[types.Part.from_text(text=user_input)],
        )
        messages.append(user_prompt_content)

        while True:
            response = client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=messages,
                config=types.GenerateContentConfig(tools=tool_specs)
            )

            if response.function_calls is None or len(response.function_calls) == 0:
                response_content = types.Content(
                    role="model",
                    parts=[{"text": response.text}]
                )
                messages.append(response_content)
                break

            for i in range(len(response.function_calls)):
                function_response_part = await pocket.ainvoke(response.function_calls[i])

                func_call_content = response.candidates[0].content
                func_response_content = types.Content(
                    role='user',
                    parts=[function_response_part],
                )
                messages.append(func_call_content)
                messages.append(func_response_content)

        for part in messages[-1].parts:
            print("response : ", part.text)


if __name__ == "__main__":
    agent()
