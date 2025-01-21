import asyncio

from hyperpocket import Pocket
from hyperpocket.auth import AuthProvider
from hyperpocket.tool import function_tool


# before starting, set slack, google oauth client id/secret in pocket setting.toml

@function_tool(
    auth_provider=AuthProvider.SLACK
)
def function_tool_with_slack_auth(**kwargs):
    """
    function tool with slack auth
    """
    # do something with SLACK_BOT_TOKEN ..

    return "success to test slack"


@function_tool(
    auth_provider=AuthProvider.GOOGLE,
    scopes=["https://www.googleapis.com/auth/calendar"]
)
def function_tool_with_google_auth(**kwargs):
    """
    function tool with google auth
    """
    # do something with GOOGLE_TOKEN

    return "success to test google"


async def main():
    pocket = Pocket(
        tools=[
            function_tool_with_slack_auth,
            function_tool_with_google_auth,
        ]
    )

    # 01. get authenticatio URI
    prepare_list = await pocket.initialize_tool_auth()

    for idx, prepare in enumerate(prepare_list):
        print(f"{idx + 1}. {prepare}")

    # 02. wait until auth is done
    await pocket.wait_tool_auth()

    # 03. tool invoke without interrupt
    slack_auth_function_result = await pocket.ainvoke(tool_name="function_tool_with_slack_auth", body={})
    google_auth_function_result = await pocket.ainvoke(tool_name="function_tool_with_google_auth", body={})

    print("slack auth function result: ", slack_auth_function_result)
    print("google auth function result: ", google_auth_function_result)


if __name__ == "__main__":
    asyncio.run(main())
