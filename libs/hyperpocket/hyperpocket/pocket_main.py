import asyncio
import concurrent.futures
from threading import Lock
from typing import Any, List, Union, Callable, Optional

from hyperpocket.builtin import get_builtin_tools
from hyperpocket.config import pocket_logger
from hyperpocket.pocket_auth import PocketAuth
from hyperpocket.server.server import PocketServer
from hyperpocket.tool import Tool, from_func
from hyperpocket.tool.dock import Dock
from hyperpocket.tool_like import ToolLike


class Pocket(object):
    server: PocketServer
    auth: PocketAuth
    tools: dict[str, Tool]

    _cnt_pocket_count: int = 0
    _pocket_count_lock = Lock()

    @staticmethod
    def _default_dock() -> Dock:
        try:
            from hyperdock_container.dock import ContainerDock
            pocket_logger.info("hyperdock-container is loaded.")
            return ContainerDock()
        except ImportError as e:
            pocket_logger.warning("Failed to import hyperdock_container.")
            raise e

    def __init__(
        self,
        tools: list[ToolLike] = None,
        auth: PocketAuth = None,
        use_profile: bool = False,
    ):
        try:
            if auth is None:
                auth = PocketAuth()
            if tools is None:
                tools = []

            self.auth = auth
            self.use_profile = use_profile
            self.server = PocketServer.get_instance()
            self.tools = {}

            self.load_tools(tools)
            pocket_logger.info(
                f"All Registered Tools Loaded successfully. total registered tools : {len(self.tools)}"
            )

            # load builtin tool
            builtin_tools = get_builtin_tools(self.auth)
            for tool in builtin_tools:
                self.tools[tool.name] = tool
            pocket_logger.info(
                f"All BuiltIn Tools Loaded successfully. total tools : {len(self.tools)}"
            )

            with Pocket._pocket_count_lock:
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

        result, paused = await self.acall(
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
        tool_by_provider = self.grouping_tool_by_auth_provider()

        prepare_list = {}
        for provider, tools in tool_by_provider.items():
            tool_name_list = [tool.name for tool in tools]
            prepare = await self.prepare_auth(
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
            tool_by_provider = self.grouping_tool_by_auth_provider()

            waiting_futures = []
            for provider, tools in tool_by_provider.items():
                if len(tools) == 0:
                    continue
                waiting_futures.append(
                    self.authenticate(
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

    async def acall(
        self,
        tool_name: str,
        body: Any,
        thread_id: str = "default",
        profile: str = "default",
        *args,
        **kwargs,
    ) -> tuple[str, bool]:
        """
        Invoke tool asynchronously, not that different from `Pocket.invoke`
        But this method is called only in subprocess.

        This function performs the following steps:
            1. `prepare_auth` : preparing the authentication process for the tool if necessary.
            2. `authenticate` : performing authentication that needs to invoke tool.
            3. `tool_call` : Executing tool actually with authentication information.

        Args:
            tool_name(str): tool name to invoke
            body(Any): tool arguments. should be json format
            thread_id(str): thread id
            profile(str): profile name

        Returns:
            tuple[str, bool]: tool result and state.
        """
        pocket_logger.debug(f"{tool_name} tool call. body: {body}")
        tool = self._tool_instance(tool_name)
        if tool.auth is not None:
            callback_info = await self.prepare_auth(tool_name, thread_id, profile, **kwargs)
            if callback_info:
                return callback_info, True
        # 02. authenticate
        credentials = await self.authenticate(tool_name, thread_id, profile, **kwargs)
        # 03. call tool
        result = await self.tool_call(tool_name, body=body, envs=credentials, **kwargs)
        pocket_logger.debug(f"{tool_name} tool call result: {result}")
        return result, False

    async def prepare_auth(
        self,
        tool_name: Union[str, List[str]],
        thread_id: str = "default",
        profile: str = "default",
        **kwargs,
    ) -> Optional[str]:
        """
        Prepares the authentication process for the tool if necessary.
        Returns callback URL and whether the tool requires authentication.

        Args:
            tool_name(Union[str,List[str]]): tool name to invoke
            thread_id(str): thread id
            profile(str): profile name

        Returns:
            Optional[str]: callback URI if necessary
        """

        if isinstance(tool_name, str):
            tool_name = [tool_name]

        tools: List[Tool] = []
        for name in tool_name:
            tool = self._tool_instance(name)
            if tool.auth is not None:
                tools.append(tool)

        if len(tools) == 0:
            return None

        auth_handler_name = tools[0].auth.auth_handler
        auth_provider = tools[0].auth.auth_provider
        auth_scopes = set()

        for tool in tools:
            if tool.auth.auth_handler != auth_handler_name:
                pocket_logger.error(
                    f"All Tools should have same auth handler. but it's different {tool.auth.auth_handler}, {auth_handler_name}"
                )

                return f"All Tools should have same auth handler. but it's different {tool.auth.auth_handler}, {auth_handler_name}"
            if tool.auth.auth_provider != auth_provider:
                pocket_logger.error(
                    f"All Tools should have same auth provider. but it's different {tool.auth.auth_provider}, {auth_provider}"
                )
                return f"All Tools should have same auth provider. but it's different {tool.auth.auth_provider}, {auth_provider}"

            if tool.auth.scopes is not None:
                auth_scopes |= set(tool.auth.scopes)

        auth_req = self.auth.make_request(
            auth_handler_name=auth_handler_name,
            auth_provider=auth_provider,
            auth_scopes=list(auth_scopes),
        )

        return await self.auth.prepare(
            auth_req=auth_req,
            auth_handler_name=auth_handler_name,
            auth_provider=auth_provider,
            thread_id=thread_id,
            profile=profile,
            **kwargs,
        )

    async def authenticate(
        self,
        tool_name: str,
        thread_id: str = "default",
        profile: str = "default",
        **kwargs,
    ) -> dict[str, str]:
        """
        Authenticates the handler included in the tool and returns credentials.

        Args:
            tool_name(str): tool name to invoke
            thread_id(str): thread id
            profile(str): profile name

        Returns:
            dict[str, str]: credentials
        """
        tool = self._tool_instance(tool_name)
        if tool.auth is None:
            return {}
        auth_req = self.auth.make_request(
            auth_handler_name=tool.auth.auth_handler,
            auth_provider=tool.auth.auth_provider,
            auth_scopes=tool.auth.scopes,
        )
        auth_ctx = await self.auth.authenticate_async(
            auth_req=auth_req,
            auth_handler_name=tool.auth.auth_handler,
            auth_provider=tool.auth.auth_provider,
            thread_id=thread_id,
            profile=profile,
            **kwargs,
        )
        return auth_ctx.to_dict()

    async def tool_call(
        self,
        tool_name: str,
        body: Any,
        thread_id: str = "default",
        profile: str = "default",
        *args,
        **kwargs,
    ):
        try:
            tool = self._tool_instance(tool_name)
            result = await asyncio.wait_for(
                tool.ainvoke(body=body, thread_id=thread_id, profile=profile, **kwargs), timeout=180)
        except asyncio.TimeoutError:
            pocket_logger.warning("Timeout tool call.")
            return "timeout tool call"

        # TODO(moon): extract
        if tool.postprocessings is not None:
            for postprocessing in tool.postprocessings:
                try:
                    result = postprocessing(result)
                except Exception as e:
                    exception_str = (
                        f"Error in postprocessing `{postprocessing.__name__}`: {e}"
                    )
                    pocket_logger.error(exception_str)
                    return exception_str

        return result

    def grouping_tool_by_auth_provider(self) -> dict[str, List[Tool]]:
        tool_by_provider = {}
        for tool_name, tool in self.tools.items():
            if tool.auth is None:
                continue

            auth_provider_name = tool.auth.auth_provider.name
            if tool_by_provider.get(auth_provider_name):
                tool_by_provider[auth_provider_name].append(tool)
            else:
                tool_by_provider[auth_provider_name] = [tool]
        return tool_by_provider

    def load_tools(self, tools: Union[List[ToolLike], ToolLike]) -> List[Tool]:
        """
        Load a list of tools into the pocket.

        This method takes a list of tool identifiers(tool like) and loads them into the
        pocket for use.

        Args:
            tools (Union[List[ToolLike], ToolLike]): A list of tool identifiers to be loaded.
        """
        if not isinstance(tools, list):
            tools = [tools]

        loaded_tools = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10, thread_name_prefix="tool-loader") as executor:
            futures = [executor.submit(self._load_tool, tool_like) for tool_like in tools]
            loaded_tools = [future.result() for future in concurrent.futures.as_completed(futures)]

        for tool in loaded_tools:
            if tool.name in self.tools:
                raise RuntimeError(f"{tool.name} already exists. duplicated tool name.")
            self.tools[tool.name] = tool

        return loaded_tools

    def _load_tool(self, tool_like) -> Tool:
        if isinstance(tool_like, str) or isinstance(tool_like, tuple):
            dock = self._default_dock()
            return dock(tool_like)
        elif isinstance(tool_like, Tool):
            return tool_like
        elif isinstance(tool_like, Callable):
            return from_func(tool_like)
        else:
            raise ValueError(f"Invalid tool type: {type(tool_like)}")

    def remove_tool(self, tool_name: str) -> bool:
        """
        Remove a tool from the pocket.

        This method removes a tool identified by the given tool_name.

        Args:
            tool_name (str): The tool name to be removed.

        Returns:
            bool: True if the tool is removed successfully, False otherwise.
        """
        if not tool_name in self.tools:
            return False
        del self.tools[tool_name]
        return True

    def _tool_instance(self, tool_name: str) -> Tool:
        return self.tools[tool_name]

    def _teardown_server(self):
        self.teardown()

    def teardown(self):
        if hasattr(self, 'server'):
            with Pocket._pocket_count_lock:
                Pocket._cnt_pocket_count -= 1
            if Pocket._cnt_pocket_count <= 0:
                self.server.teardown()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()
