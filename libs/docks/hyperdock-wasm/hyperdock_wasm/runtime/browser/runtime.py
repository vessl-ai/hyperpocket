import asyncio
import json
import pathlib
from typing import Any, Optional

from hyperdock_wasm.runtime.browser.invoker import Invoker
from hyperdock_wasm.runtime.browser.invoker_browser import InvokerBrowser
from hyperdock_wasm.runtime.browser.script import ScriptRuntime
from hyperdock_wasm.runtime.runtime import ToolRuntime
from hyperdock_wasm.tool import WasmToolRequest
from hyperpocket.auth import AuthProvider
from hyperpocket.tool import ToolAuth
from hyperpocket.tool.function import FunctionTool


class BrowserScriptRuntime(ToolRuntime):
    _browser: Optional[InvokerBrowser]
    _invoker: Optional[Invoker]

    def __init__(self):
        self._browser = None
        self._invoker = None

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
        toolpkg_path = tool_req.tool_ref.toolpkg_path()
        rel_path = tool_req.rel_path
        rootpath = pathlib.Path(toolpkg_path) / rel_path
        pocket_tool_config_path = rootpath / "pocket.json"

        with pocket_tool_config_path.open("r") as f:
            pocket_tool_config = json.load(f)
            default_tool_vars = dict()

            # 1. Tool section
            mcp_tool_config = pocket_tool_config["tool"]
            name = mcp_tool_config["name"]
            description = mcp_tool_config.get("description", "")
            json_schema = mcp_tool_config.get("inputSchema", {})

            # 2. language section
            if language := pocket_tool_config.get("language"):
                lang = language.lower()
                if lang == "python":
                    runtime = ScriptRuntime.Python
                elif lang == "node":
                    runtime = ScriptRuntime.Node
                else:
                    raise ValueError(f"The language `{lang}` is not supported.")
            else:
                raise ValueError("`language` field is required in config.toml")

            # 3. variable section
            default_tool_vars = pocket_tool_config.get("variables", {})

            # 4. auth section
            auth = None
            if (_auth := pocket_tool_config.get("auth")) is not None:
                auth_provider = _auth["auth_provider"]
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

        tool = FunctionTool.from_func(
            func=_invoke,
            afunc=_ainvoke,
            auth=auth,
            name=name,
            description=description,
            json_schema=json_schema,
            tool_vars=default_tool_vars,
            keep_structured_arguments=True,
        )
        if tool_req.overridden_tool_vars is not None:
            tool.override_tool_variables(tool_req.overridden_tool_vars)
        return tool
