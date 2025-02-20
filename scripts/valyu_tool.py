import os
from hyperpocket_openai import PocketOpenAI

def main():
    # Remove Docker configuration since we're using WASM
    pocket = PocketOpenAI(
        tools=[
            '/Users/yorkeccak/Development/Valyu/integrations/hyperpocket/tools/valyu/get-context'
        ]
    )

    tools = pocket.get_open_ai_tool_specs()

    response = llm.chat.completions.create(
        model="gpt-4o",
        tools=tools,
        messages=[
            {
                "role": "user",
                "content": "What is portfolio theory in finance and who created it?"
            }
        ]
    )

    print(response)

if __name__ == '__main__':
    main()