import os
import json
import pathlib
from dotenv import dotenv_values
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

    def __init__(self, lock: Lock, rel_path: str):
        self.lock = lock
        self.rel_path = rel_path

    def __str__(self):
        return f"ToolRequest(lock={self.lock}, rel_path={self.rel_path})"


def from_local(path: str) -> WasmToolRequest:
    return WasmToolRequest(LocalLock(path), "")


def from_git(repository: str, ref: str, rel_path: str) -> WasmToolRequest:
    return WasmToolRequest(GitLock(repository_url=repository, git_ref=ref), rel_path)


def from_github(owner: str, repo: str, ref: str, rel_path: str) -> WasmToolRequest:
    repository = f"https://github.com/{owner}/{repo}"
    return from_git(repository, ref, rel_path)


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
    def from_tool_request(cls, tool_req: WasmToolRequest, lockfile: Lockfile = None, **kwargs) -> 'WasmTool':
        if not lockfile:
            raise ValueError("lockfile is required")
        tool_req.lock = lockfile.get_lock(tool_req.lock.key())
        toolpkg_path = tool_req.lock.toolpkg_path()
        rel_path = tool_req.rel_path
        rootpath = pathlib.Path(toolpkg_path) / rel_path
        schema_path = rootpath / "schema.json"
        config_path = rootpath / "config.toml"
        readme_path = rootpath / "README.md"
        envvar_path = rootpath / ".env"

        try:
            with schema_path.open("r") as f:
                json_schema = json.load(f)
        except Exception as e:
            pocket_logger.warning(f"{toolpkg_path} failed to load json schema. error : {e}")
            json_schema = None

        try:
            with config_path.open("r") as f:
                config = toml.load(f)
                name = config.get('name')
                description = config.get('description')
                if language := config.get('language'):
                    lang = language.lower()
                    if lang == 'python':
                        runtime = ScriptRuntime.Python
                    elif lang == 'node':
                        runtime = ScriptRuntime.Node
                    else:
                        raise ValueError(f"The language `{lang}` is not supported.")
                else:
                    raise ValueError("`language` field is required in config.toml")
                auth = cls._get_auth(config)
        except Exception as e:
            raise ValueError(f"Failed to load config.toml: {e}")

        if readme_path.exists():
            with readme_path.open("r") as f:
                readme = f.read()
        else:
            readme = None
        
        if envvar_path.exists():
            cls._inject_envvar(envvar_path)
            
        return cls(
            name=name,
            description=description,
            argument_json_schema=json_schema,
            auth=auth,
            runtime=runtime,
            readme=readme,
            pkg_lock=tool_req.lock,
            rel_path=tool_req.rel_path,
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
    
    @classmethod
    def _inject_envvar(cls, envvar_path: pathlib.Path) -> None:
        current_env_path = pathlib.Path(os.getcwd()) / ".env"
        current_env = dotenv_values(current_env_path)
        tool_env = dotenv_values(envvar_path)
        not_found_envvars = []

        for k, v in tool_env.items():
            if k in current_env:
                tool_env[k] = current_env[k]
            else:
                not_found_envvars.append(k)

        for k in not_found_envvars:
            print(f"The following environment variables {k} are not found in the current environment:")
            print(f"Please add the following environment variables to the current environment:")
            user_input = input(f"{k}: ")
            if user_input:
                tool_env[k] = user_input

        with open(envvar_path, "w") as f:
            for k, v in tool_env.items():
                f.write(f"{k}={v}\n")
    
    def template_arguments(self) -> dict[str, str]:
        return {}

    def invoke(self, body: Any, envs: dict, **kwargs) -> str:
        return self.invoker.invoke(
            str(self.pkg_lock.toolpkg_path() / self.rel_path),
            self.runtime,
            body,
            envs,
            **kwargs,
        )

    async def ainvoke(self, body: Any, envs: dict, **kwargs) -> str:
        return await self.invoker.ainvoke(
            str(self.pkg_lock.toolpkg_path() / self.rel_path),
            self.runtime,
            body,
            envs,
            **kwargs,
        )
