import asyncio
from typing import Any, List, Union

from hyperpocket.config import pocket_logger
from hyperpocket.pocket_auth import PocketAuth
from hyperpocket.pocket_core import PocketCore
from hyperpocket.server.server import PocketServer
from hyperpocket.tool_like import ToolLike


class Pocket(object):
    server: PocketServer
    core: PocketCore

    _cnt_pocket_count: int = 0

    def __init__(
        self,
        tools: list[ToolLike],
        auth: PocketAuth = None,
        use_profile: bool = False,
    ):
        try:
            self.use_profile = use_profile
            self.server = PocketServer.get_instance()
            self.core = PocketCore(
                tools=tools,
                auth=auth,
            )
            Pocket._cnt_pocket_count += 1
        except Exception as e:
            self.teardown()
            pocket_logger.error(f"Failed to initialize pocket server. error : {e}")
            raise e

    def invoke(
        self,
        tool_name: str,
        body: Any,
        thread_id: str = "default",
        profile: str = "default",
        *args,
        **kwargs,
    ) -> str:
        """
        Invoke Tool synchronously

        Args:
            tool_name(str): tool name to invoke
            body(Any): tool arguments. should be json format
            thread_id(str): thread id
            profile(str): profile name

        Returns:
            str: tool result
        """
        return asyncio.run(
            self.ainvoke(tool_name, body, thread_id, profile, *args, **kwargs)
        )

    async def ainvoke(
        self,
        tool_name: str,
        body: Any,
        thread_id: str = "default",
        profile: str = "default",
        *args,
        **kwargs,
    ) -> str:
        """
        Invoke Tool asynchronously

        Args:
            tool_name(str): tool name to invoke
            body(Any): tool arguments. should be json format
            thread_id(str): thread id
            profile(str): profile name

        Returns:
            str: tool result
        """
        result, _ = await self.ainvoke_with_state(
            tool_name=tool_name,
            body=body,
            thread_id=thread_id,
            profile=profile,
            *args,
            **kwargs,
        )
        pocket_logger.debug(f"{tool_name} result: {result}")
        return result

    def invoke_with_state(
        self,
        tool_name: str,
        body: Any,
        thread_id: str = "default",
        profile: str = "default",
        *args,
        **kwargs,
    ) -> tuple[str, bool]:
        """
        Invoke Tool with state synchronously
        State indicates whether this tool is paused or not.
        If the tool needs user's interaction or waiting for some process, this tool is paused.

        Args:
            tool_name(str): tool name to invoke
            body(Any): tool arguments. should be json format
            thread_id(str): thread id
            profile(str): profile name

        Returns:
            tuple[str, bool]: tool result and state.
        """
        try:
            loop = asyncio.new_event_loop()
        except RuntimeError:
            pocket_logger.warning(
                "Can't execute sync def in event loop. use nest-asyncio"
            )

            import nest_asyncio

            loop = asyncio.new_event_loop()
            nest_asyncio.apply(loop=loop)

        result = loop.run_until_complete(
            self.ainvoke_with_state(
                tool_name, body, thread_id, profile, *args, **kwargs
            )
        )

        return result

    async def ainvoke_with_state(
        self,
        tool_name: str,
        body: Any,
        thread_id: str = "default",
        profile: str = "default",
        *args,
        **kwargs,
    ) -> tuple[str, bool]:
        """
        Invoke Tool with state synchronously
        State indicates whether this tool is paused or not.
        If the tool needs user's interaction or waiting for some process, this tool is paused.

        Args:
            tool_name(str): tool name to invoke
            body(Any): tool arguments. should be json format
            thread_id(str): thread id
            profile(str): profile name

        Returns:
            tuple[str, bool]: tool result and state.
        """
        _kwargs = {
            "tool_name": tool_name,
            "body": body,
            "thread_id": thread_id,
            "profile": profile,
            **kwargs,
        }

        result, paused = await self.core.acall(
            tool_name=tool_name,
            body=body,
            thread_id=thread_id,
            profile=profile,
            **kwargs
        )
        if not isinstance(result, str):
            result = str(result)

        return result, paused

    async def initialize_tool_auth(
        self,
        thread_id: str = "default",
        profile: str = "default",
    ) -> dict[str, str]:
        """
        Initialize authentication for all tools.

        This method prepares all tools that require authentication by retrieving
        their respective authentication URIs.

        If no tool requires authentication, an empty list is returned.

        Args:
            thread_id (str): The thread id. Defaults to 'default'.
            profile (str): The profile to be used for authentication. Defaults to 'default'.

        Returns:
            List[str]: A list of authentication URIs for the tools that require authentication.
        """
        tool_by_provider = self.core.grouping_tool_by_auth_provider()

        prepare_list = {}
        for provider, tools in tool_by_provider.items():
            tool_name_list = [tool.name for tool in tools]
            prepare = self.core.prepare_auth(
                tool_name=tool_name_list,
                thread_id=thread_id,
                profile=profile,
            )
            if prepare is not None:
                prepare_list[provider] = prepare

        return prepare_list

    async def wait_tool_auth(
        self, thread_id: str = "default", profile: str = "default"
    ) -> bool:
        """
        Wait until all tool authentications are completed.

        This method waits until all tools associated with the given
        `thread_id` and `profile` have completed their authentication process.

        Args:
            thread_id (str): The thread id. Defaults to 'default'.
            profile (str): The profile to be used for authentication. Defaults to 'default'.

        Returns:
            bool: Returns `True` if all tool authentications are successfully completed,
            or `False` if the process was interrupted or failed.
        """
        try:
            tool_by_provider = self.core.grouping_tool_by_auth_provider()

            waiting_futures = []
            for provider, tools in tool_by_provider.items():
                if len(tools) == 0:
                    continue
                waiting_futures.append(
                    self.core.authenticate(
                        tool_name=tools[0].name,
                        thread_id=thread_id,
                        profile=profile,
                    )
                )

            await asyncio.gather(*waiting_futures)

            return True

        except asyncio.TimeoutError as e:
            pocket_logger.error("authentication time out.")
            raise e

    async def prepare_auth(
        self,
        tool_name: Union[str, List[str]],
        thread_id: str = "default",
        profile: str = "default",
        *args,
        **kwargs,
    ):
        prepare = self.core.prepare_auth(
            tool_name=tool_name,
            thread_id=thread_id,
            profile=profile,
            **kwargs,
        )

        return prepare

    async def authenticate(
        self,
        tool_name: str,
        thread_id: str = "default",
        profile: str = "default",
        *args,
        **kwargs,
    ):
        credentials = await self.core.authenticate(
            tool_name=tool_name,
            thread_id=thread_id,
            profile=profile,
            **kwargs,
        )

        return credentials

    async def tool_call(
        self,
        tool_name: str,
        body: Any,
        thread_id: str = "default",
        profile: str = "default",
        *args,
        **kwargs,
    ):
        result = await self.core.tool_call(
            tool_name, body=body,
            thread_id=thread_id,
            profile=profile,
            **kwargs
        )

        return result

    def _teardown_server(self):
        self.teardown()

    def teardown(self):
        if hasattr(self, 'server'):
            Pocket._cnt_pocket_count -= 1
            if Pocket._cnt_pocket_count <= 0:
                self.server.teardown()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()
