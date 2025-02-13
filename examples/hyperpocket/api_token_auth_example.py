import asyncio

from hyperpocket import Pocket
from hyperpocket.auth import AuthProvider
from hyperpocket.tool import function_tool


@function_tool(
    auth_provider=AuthProvider.APITOKEN,
)
def function_tool_with_api_token_auth(**kwargs):
    """
    function tool with api token auth
    """

    api_token = kwargs.get("API_TOKEN")
    print(f"api token: {api_token}")

    ## do something with api token

    return "success to test api token auth"


async def main():
    pocket = Pocket(
        tools=[
            function_tool_with_api_token_auth,
        ]
    )

    # 01. get authenticatio URI
    prepare_list = await pocket.initialize_tool_auth()

    for idx, prepare in enumerate(prepare_list):
        print(f"{idx + 1}. {prepare}")

    # 02. wait until auth is done
    await pocket.wait_tool_auth()

    # 03. tool invoke without interrupt
    api_token_auth_function_result = await pocket.ainvoke(
        tool_name="function_tool_with_api_token_auth", body={}
    )

    print("api token auth function result: ", api_token_auth_function_result)


if __name__ == "__main__":
    asyncio.run(main())
