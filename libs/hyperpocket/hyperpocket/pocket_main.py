import asyncio
import pathlib
from typing import Union, Any, Optional, Callable, List

from hyperpocket.auth import AuthProvider
from hyperpocket.config import pocket_logger
from hyperpocket.pocket_auth import PocketAuth
from hyperpocket.repository import Lockfile
from hyperpocket.repository.lock import LocalLock, GitLock
from hyperpocket.server.server import PocketServer, PocketServerOperations
from hyperpocket.session.interface import BaseSessionValue
from hyperpocket.tool import Tool, ToolRequest, from_func
from hyperpocket.tool.function.tool import FunctionTool
from hyperpocket.tool.wasm import WasmTool
from hyperpocket.tool.wasm.tool import WasmToolRequest

ToolLike = Union[Tool, str, Callable, ToolRequest]


class Pocket(object):
    auth: PocketAuth
    server: PocketServer
    tools: dict[str, Tool]

    def __init__(self,
                 tools: list[ToolLike],
                 auth: PocketAuth = None,
                 lockfile_path: Optional[str] = None,
                 force_update: bool = False):
        if auth is None:
            auth = PocketAuth()
        self.auth = auth

        if lockfile_path is None:
            lockfile_path = "./pocket.lock"
        lockfile_pathlib_path = pathlib.Path(lockfile_path)
        lockfile = Lockfile(lockfile_pathlib_path)
        tool_likes = []
        for tool_like in tools:
            if isinstance(tool_like, str):
                if pathlib.Path(tool_like).exists():
                    lock = LocalLock(tool_like)
                    req = WasmToolRequest(lock, "")
                else:
                    lock = GitLock(repository_url=tool_like, git_ref='HEAD')
                    req = WasmToolRequest(lock, "")
                lockfile.add_lock(lock)
                tool_likes.append(req)
            elif isinstance(tool_like, WasmToolRequest):
                lockfile.add_lock(tool_like.lock)
                tool_likes.append(tool_like)
            elif isinstance(tool_like, ToolRequest):
                raise ValueError(f"unreachable. tool_like:{tool_like}")
            elif isinstance(tool_like, WasmTool):
                raise ValueError("WasmTool should pass ToolRequest instance instead.")
            else:
                tool_likes.append(tool_like)
        lockfile.sync(force_update=force_update, referenced_only=True)

        self.tools = dict()
        for tool_like in tool_likes:
            tool = self._load_tool(tool_like, lockfile)
            if tool.name in self.tools:
                pocket_logger.error(f"Duplicate tool name: {tool.name}.")
                raise ValueError(f"Duplicate tool name: {tool.name}")
            self.tools[tool.name] = tool

        pocket_logger.info(f"All Registered Tools Loaded successfully. total registered tools : {len(self.tools)}")

        builtin_tools = get_builtin_tools(self.auth)
        for tool in builtin_tools:
            self.tools[tool.name] = tool
        pocket_logger.info(f"All BuiltIn Tools Loaded successfully. total tools : {len(self.tools)}")

        self.server = PocketServer()
        self.server.run(self)

    def _load_tool(self, tool_like: ToolLike, lockfile: Lockfile) -> Tool:
        pocket_logger.info(f"Loading Tool {tool_like}")
        if isinstance(tool_like, Tool):
            tool = tool_like
        elif isinstance(tool_like, ToolRequest):
            tool = Tool.from_tool_request(tool_like, lockfile=lockfile)
        elif isinstance(tool_like, Callable):
            tool = FunctionTool.from_func(tool_like)
        else:
            raise ValueError(f"Invalid tool type: {type(tool_like)}")

        pocket_logger.info(f"Complete Loading Tool {tool.name}")
        return tool

    def invoke(self,
               tool_name: str,
               body: Any,
               thread_id: str = 'default',
               profile: str = 'default',
               *args, **kwargs) -> str:
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
        result = asyncio.run(self.ainvoke(tool_name, body, thread_id, profile, *args, **kwargs))
        return result

    async def ainvoke(self,
                      tool_name: str,
                      body: Any,
                      thread_id: str = 'default',
                      profile: str = 'default',
                      *args, **kwargs) -> str:
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
        return result

    def invoke_with_state(self,
                          tool_name: str,
                          body: Any,
                          thread_id: str = 'default',
                          profile: str = 'default',
                          *args, **kwargs) -> tuple[str, bool]:
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
            result = loop.run_until_complete(
                self.ainvoke_with_state(tool_name, body, thread_id, profile, *args, **kwargs))

        except RuntimeError as e:
            pocket_logger.warning("Can't execute sync def in event loop. use nest-asyncio")

            import nest_asyncio
            loop = asyncio.new_event_loop()
            nest_asyncio.apply(loop=loop)

            result = loop.run_until_complete(
                self.ainvoke_with_state(tool_name, body, thread_id, profile, *args, **kwargs))

        return result

    async def ainvoke_with_state(self,
                                 tool_name: str,
                                 body: Any,
                                 thread_id: str = 'default',
                                 profile: str = 'default',
                                 *args, **kwargs) -> tuple[str, bool]:
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
        result, paused = await self.server.call_in_subprocess(
            PocketServerOperations.CALL,
            args,
            {
                'tool_name': tool_name,
                'body': body,
                'thread_id': thread_id,
                'profile': profile,
                **kwargs,
            },
        )
        if not isinstance(result, str):
            result = str(result)

        return result, paused

    # DO NOT EVER THINK ABOUT USING SERVER PROPERTY BELOW HERE
    async def acall(self,
                    tool_name: str,
                    body: Any,
                    thread_id: str = 'default',
                    profile: str = 'default',
                    *args, **kwargs) -> tuple[str, bool]:
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

    def prepare_auth(self,
                     tool_name: str,
                     thread_id: str = 'default',
                     profile: str = 'default',
                     **kwargs) -> Optional[str]:
        """
        Prepares the authentication process for the tool if necessary.
        Returns callback URL and whether the tool requires authentication.

        Args:
            tool_name(str): tool name to invoke
            thread_id(str): thread id
            profile(str): profile name

        Returns:
            Optional[str]: callback URI if necessary
        """
        tool = self._tool_instance(tool_name)
        if tool.auth is None:
            return None

        auth_req = self.auth.make_request(
            auth_handler_name=tool.auth.auth_handler,
            auth_provider=tool.auth.auth_provider,
            auth_scopes=tool.auth.scopes)

        return self.auth.prepare(
            auth_req=auth_req,
            auth_handler_name=tool.auth.auth_handler,
            auth_provider=tool.auth.auth_provider,
            thread_id=thread_id,
            profile=profile,
            **kwargs
        )

    async def authenticate(
            self,
            tool_name: str,
            thread_id: str = 'default',
            profile: str = 'default',
            **kwargs) -> dict[str, str]:
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
            auth_scopes=tool.auth.scopes)
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

    def _tool_instance(self, tool_name: str) -> Tool:
        return self.tools[tool_name]

    def _teardown_server(self):
        self.server.teardown()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.__dict__.get('server'):
            self.server.teardown()

    def __del__(self):
        if self.__dict__.get('server'):
            self.server.teardown()

    def __getstate__(self):
        state = self.__dict__.copy()
        if 'server' in state:
            del state['server']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


def get_builtin_tools(pocket_auth: PocketAuth) -> List[Tool]:
    """
    Get Builtin Tools

    Builtin Tool can access to Pocket Core.
    """

    def __get_current_thread_session_state(thread_id: str) -> List[BaseSessionValue]:
        """
        Get current authentication session list in the thread.

        The output format should be like this

        - [AUTH PROVIDER] [state] [scopes, ...] : some explanation ..
        - [AUTH PROVIDER] [state] [scopes, ...] : some explanation ..
        - [AUTH PROVIDER] [state] [scopes, ...] : some explanation ..
        ...

        Args:
            thread_id(str): thread id

        Returns:

        """
        session_list = pocket_auth.list_session_state(thread_id)
        return session_list

    def __delete_session(auth_provider_name: str, thread_id: str = "default", profile: str = "default") -> bool:
        """
        Delete Session in thread

        Args:
            auth_provider_name(str): auth provider name
            thread_id(str): thread id
            profile(str): profile name

        Returns:
            bool: Flag indicating success or failure
        """

        auth_provider = AuthProvider.get_auth_provider(auth_provider_name)
        return pocket_auth.delete_session(auth_provider, thread_id, profile)

    builtin_tools = [
        from_func(func=__get_current_thread_session_state),
        from_func(func=__delete_session),
    ]

    return builtin_tools
