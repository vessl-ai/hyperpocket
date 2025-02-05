import asyncio
import pathlib
from typing import Any, Callable, List, Optional, Union

from hyperpocket.builtin import get_builtin_tools
from hyperpocket.config import pocket_logger
from hyperpocket.pocket_auth import PocketAuth
from hyperpocket.repository import Lockfile
from hyperpocket.repository.lock import GitLock, LocalLock
from hyperpocket.tool import Tool, ToolRequest
from hyperpocket.tool.function import from_func
from hyperpocket.tool.wasm import WasmTool
from hyperpocket.tool.wasm.tool import WasmToolRequest
from hyperpocket.tool_like import ToolLike


class PocketCore:
    auth: PocketAuth
    tools: dict[str, Tool]
    lockfile: Lockfile

    def __init__(
        self,
        tools: list[ToolLike],
        auth: PocketAuth = None,
        lockfile_path: Optional[str] = None,
        force_update: bool = False,
    ):
        if auth is None:
            auth = PocketAuth()
        self.auth = auth

        # init lockfile
        if lockfile_path is None:
            lockfile_path = "./pocket.lock"
        lockfile_pathlib_path = pathlib.Path(lockfile_path)
        self.lockfile = Lockfile(lockfile_pathlib_path)

        # parse tool_likes and add lock of the tool like to the lockfile
        tool_likes = []
        for tool_like in tools:
            parsed_tool_like = self._parse_tool_like(tool_like)
            tool_likes.append(parsed_tool_like)
            self._add_tool_like_lock_to_lockfile(parsed_tool_like)
        self.lockfile.sync(force_update=force_update, referenced_only=True)

        # load tool from tool_like
        self.tools = dict()
        for tool_like in tool_likes:
            self._load_tool(tool_like)

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
        tool = self._tool_instance(tool_name)
        if tool.auth is not None:
            callback_info = self.prepare_auth(tool_name, thread_id, profile, **kwargs)
            if callback_info:
                return callback_info, True
        # 02. authenticate
        credentials = await self.authenticate(tool_name, thread_id, profile, **kwargs)
        # 03. call tool
        result = await self.tool_call(tool_name, body=body, envs=credentials, **kwargs)
        return result, False

    def prepare_auth(
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

        return self.auth.prepare(
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

    def _load_tool(self, tool_like: ToolLike) -> Tool:
        pocket_logger.info(f"Loading Tool {tool_like}")
        if isinstance(tool_like, Tool):
            tool = tool_like
        elif isinstance(tool_like, ToolRequest):
            tool = Tool.from_tool_request(tool_like, lockfile=self.lockfile)
        elif isinstance(tool_like, Callable):
            tool = from_func(tool_like)
        else:
            raise ValueError(f"Invalid tool type: {type(tool_like)}")

        if tool.name in self.tools:
            pocket_logger.error(f"Duplicate tool name: {tool.name}.")
            raise ValueError(f"Duplicate tool name: {tool.name}")
        self.tools[tool.name] = tool

        pocket_logger.info(f"Complete Loading Tool {tool.name}")
        return tool

    def _add_tool_like_lock_to_lockfile(self, tool_like: ToolLike):
        if isinstance(tool_like, WasmToolRequest):  # lock is only in WasmToolRequest
            self.lockfile.add_lock(tool_like.lock)
        return

    @classmethod
    def _parse_tool_like(cls, tool_like: ToolLike) -> ToolLike:
        if isinstance(tool_like, str):
            return cls._parse_str_tool_like(tool_like)

        elif isinstance(tool_like, WasmToolRequest):
            return tool_like

        elif isinstance(tool_like, ToolRequest):
            raise ValueError(f"unreachable. tool_like:{tool_like}")
        elif isinstance(tool_like, WasmTool):
            raise ValueError("WasmTool should pass ToolRequest instance instead.")
        else:  # Callable, Tool
            return tool_like

    @classmethod
    def _parse_str_tool_like(cls, tool_like: str) -> ToolLike:
        if pathlib.Path(tool_like).exists():
            lock = LocalLock(tool_like)
            parsed_tool_like = WasmToolRequest(lock=lock, rel_path="", tool_vars={})
        elif tool_like.startswith("https://github.com"):
            base_repo_url, git_ref, rel_path = GitLock.parse_repo_url(
                repo_url=tool_like
            )
            lock = GitLock(repository_url=base_repo_url, git_ref=git_ref)
            parsed_tool_like = WasmToolRequest(lock=lock, rel_path=rel_path, tool_vars={})
        else:
            parsed_tool_like = None
            RuntimeError(
                f"Can't convert to ToolRequest. it might be wrong github url or local path. path: {tool_like}")

        return parsed_tool_like

