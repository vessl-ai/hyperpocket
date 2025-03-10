import asyncio
import concurrent.futures
from typing import Any, Callable, List, Optional, Union, Type

from hyperpocket.builtin import get_builtin_tools
from hyperpocket.config import pocket_logger
from hyperpocket.pocket_auth import PocketAuth
from hyperpocket.tool import Tool
from hyperpocket.tool.dock import Dock
from hyperpocket.tool.function import from_func
from hyperpocket.tool_like import ToolLike


class PocketCore:
    auth: PocketAuth
    tools: dict[str, Tool]

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
        tools: list[ToolLike],
        auth: PocketAuth = None,
    ):
        if auth is None:
            auth = PocketAuth()
        self.auth = auth

        self._load_tools(tools)
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

    def _load_tools(self, tools):
        self.tools = dict()
        dock = self._default_dock()

        def _load(tool_like):
            if isinstance(tool_like, str) or isinstance(tool_like, tuple):
                return dock(tool_like)
            elif isinstance(tool_like, Tool):
                return tool_like
            elif isinstance(tool_like, Callable):
                return from_func(tool_like)
            else:
                raise ValueError(f"Invalid tool type: {type(tool_like)}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10, thread_name_prefix="tool-loader") as executor:
            futures = [executor.submit(_load, tool_like) for tool_like in tools]
            for future in concurrent.futures.as_completed(futures):
                tool = future.result()
                self.tools[tool.name] = tool

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

    async def tool_call(self, tool_name: str, **kwargs) -> str:
        """
        Executing tool actually

        Args:
            tool_name(str): tool name to invoke
            kwargs(dict): keyword arguments. authentication information is passed through this.

        Returns:
            str: tool result
        """
        tool = self._tool_instance(tool_name)
        try:
            result = await asyncio.wait_for(tool.ainvoke(**kwargs), timeout=180)
        except asyncio.TimeoutError:
            pocket_logger.warning("Timeout tool call.")
            return "timeout tool call"

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

    def _tool_instance(self, tool_name: str) -> Tool:
        return self.tools[tool_name]
