import asyncio
import json
import pathlib
from typing import Any, Optional

import toml
from hyperpocket.auth import AuthProvider
from hyperpocket.config import pocket_logger
from hyperpocket.tool import ToolAuth
from hyperpocket.tool.function import FunctionTool

from hyperdock_wasm import WasmToolRequest
from hyperdock_wasm.runtime.browser.invoker import Invoker
from hyperdock_wasm.runtime.browser.invoker_browser import InvokerBrowser
from hyperdock_wasm.runtime.browser.script import ScriptRuntime
from hyperdock_wasm.runtime.runtime import ToolRuntime


class BrowserScriptRuntime(ToolRuntime):
    _browser: Optional[InvokerBrowser]
    _invoker: Optional[Invoker]
    
    def __init__(self):
        pass
    
    async def invoker(self) -> Invoker:
        if self._invoker is None:
            self._browser = await InvokerBrowser.async_init()
            self._invoker = Invoker(self._browser)
        return self._invoker
    
    async def teardown(self):
        if self._browser is not None:
            await self._browser.teardown()

    def from_tool_request(
        self, tool_req: WasmToolRequest,
    ) -> FunctionTool:
        toolpkg_path = tool_req.lock.toolpkg_path()
        rel_path = tool_req.rel_path
        rootpath = pathlib.Path(toolpkg_path) / rel_path
        schema_path = rootpath / "schema.json"
        config_path = rootpath / "config.toml"

        try:
            with schema_path.open("r") as f:
                json_schema = json.load(f)
        except Exception as e:
            pocket_logger.warning(
                f"{toolpkg_path} failed to load json schema. error : {e}"
            )
            json_schema = None

        default_tool_vars = dict()
        try:
            with config_path.open("r") as f:
                config = toml.load(f)
                name = config.get("name")
                description = config.get("description")
                if language := config.get("language"):
                    lang = language.lower()
                    if lang == "python":
                        runtime = ScriptRuntime.Python
                    elif lang == "node":
                        runtime = ScriptRuntime.Node
                    else:
                        raise ValueError(f"The language `{lang}` is not supported.")
                else:
                    raise ValueError("`language` field is required in config.toml")
                default_tool_vars = config.get("tool_vars", {})
        except Exception as e:
            raise ValueError(f"Failed to load config.toml: {e}")
        
        auth = None
        if (_auth := config.get("auth")) is not None:
            auth_provider = _auth.get("auth_provider")
            auth_handler = _auth.get("auth_handler")
            scopes = _auth.get("scopes", [])
            auth = ToolAuth(
                auth_provider=AuthProvider.get_auth_provider(auth_provider),
                auth_handler=auth_handler,
                scopes=scopes,
            )

        async def _ainvoke(body: Any, envs: dict, **kwargs) -> str:
            invoker = await self.invoker()
            return await invoker.ainvoke(
                str(toolpkg_path / rel_path),
                runtime,
                body,
                envs,
                **kwargs,
            )
        
        def _invoke(body: Any, envs: dict, **kwargs) -> str:
            try:
                loop = asyncio.get_running_loop()
                return loop.run_until_complete(_ainvoke(body, envs, **kwargs))
            except RuntimeError:
                return asyncio.run(_ainvoke(body, envs, **kwargs))
        
        _ainvoke.__name__ = name
        _ainvoke.__doc__ = description
        _ainvoke.__model__ = json_schema
        _invoke.__name__ = name
        _invoke.__doc__ = description
        _invoke.__model__ = json_schema
        
        tool = FunctionTool.from_func(
            func=_invoke,
            afunc=_ainvoke,
            auth=auth,
            tool_vars=default_tool_vars,
            keep_structured_arguments=True,
        )
        if tool_req.overridden_tool_vars is not None:
            tool.override_tool_variables(tool_req.overridden_tool_vars)
        return tool
