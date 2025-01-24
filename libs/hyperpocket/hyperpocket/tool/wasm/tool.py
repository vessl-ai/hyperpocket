import json
import pathlib
from typing import Any, Optional

import toml

from hyperpocket.auth import AuthProvider
from hyperpocket.config import pocket_logger
from hyperpocket.repository import Lock, Lockfile
from hyperpocket.repository.lock import GitLock, LocalLock
from hyperpocket.tool import Tool, ToolRequest
from hyperpocket.tool.tool import ToolAuth
from hyperpocket.tool.wasm.invoker import WasmInvoker
from hyperpocket.tool.wasm.script import ScriptRuntime


class WasmToolRequest(ToolRequest):
    lock: Lock
    rel_path: str

    def __init__(self, lock: Lock, rel_path: str, tool_vars: dict):
        self.lock = lock
        self.rel_path = rel_path
        self.overridden_tool_vars = tool_vars

    def __str__(self):
        return f"ToolRequest(lock={self.lock}, rel_path={self.rel_path})"


def from_local(
    path: str, tool_vars: Optional[dict[str, str]] = None
) -> WasmToolRequest:
    if tool_vars is None:
        tool_vars = dict()
    return WasmToolRequest(LocalLock(path), "", tool_vars)


def from_git(
    repository: str, ref: str, rel_path: str, tool_vars: Optional[dict[str, str]] = None
) -> WasmToolRequest:
    if not tool_vars:
        tool_vars = dict()
    return WasmToolRequest(
        GitLock(repository_url=repository, git_ref=ref), rel_path, tool_vars
    )


class WasmTool(Tool):
    """
    WasmTool is Tool executing local python method.
    """

    _invoker: WasmInvoker = None
    pkg_lock: Lock = None
    rel_path: str
    runtime: ScriptRuntime = None
    json_schema: Optional[dict] = None
    readme: Optional[str] = None

    @property
    def invoker(self) -> WasmInvoker:
        if not self._invoker:
            self._invoker = WasmInvoker()
        return self._invoker

    @classmethod
    def from_tool_request(
        cls, tool_req: WasmToolRequest, lockfile: Lockfile = None, **kwargs
    ) -> "WasmTool":
        if not lockfile:
            raise ValueError("lockfile is required")
        tool_req.lock = lockfile.get_lock(tool_req.lock.key())
        toolpkg_path = tool_req.lock.toolpkg_path()
        rel_path = tool_req.rel_path
        rootpath = pathlib.Path(toolpkg_path) / rel_path
        schema_path = rootpath / "schema.json"
        config_path = rootpath / "config.toml"
        readme_path = rootpath / "README.md"

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
                auth = cls._get_auth(config)
                default_tool_vars = config.get("tool_vars", {})
        except Exception as e:
            raise ValueError(f"Failed to load config.toml: {e}")

        if readme_path.exists():
            with readme_path.open("r") as f:
                readme = f.read()
        else:
            readme = None

        return cls(
            name=name,
            description=description,
            argument_json_schema=json_schema,
            auth=auth,
            runtime=runtime,
            readme=readme,
            pkg_lock=tool_req.lock,
            rel_path=tool_req.rel_path,
            postprocessings=tool_req.postprocessings,
            default_tool_vars=default_tool_vars,
            overridden_tool_vars=tool_req.overridden_tool_vars,
        )

    @classmethod
    def _get_auth(cls, config: dict) -> Optional[ToolAuth]:
        auth = config.get("auth")
        if not auth:
            return
        auth_provider = auth.get("auth_provider")
        auth_handler = auth.get("auth_handler")
        scopes = auth.get("scopes", [])
        return ToolAuth(
            auth_provider=AuthProvider.get_auth_provider(auth_provider),
            auth_handler=auth_handler,
            scopes=scopes,
        )

    def template_arguments(self) -> dict[str, str]:
        return {}

    def invoke(self, body: Any, envs: dict, **kwargs) -> str:
        return self.invoker.invoke(
            str(self.pkg_lock.toolpkg_path() / self.rel_path),
            self.runtime,
            body,
            envs | self.tool_vars,
            **kwargs,
        )

    async def ainvoke(self, body: Any, envs: dict, **kwargs) -> str:
        return await self.invoker.ainvoke(
            str(self.pkg_lock.toolpkg_path() / self.rel_path),
            self.runtime,
            body,
            envs | self.tool_vars,
            **kwargs,
        )
