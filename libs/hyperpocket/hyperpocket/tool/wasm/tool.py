import os
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

    def __init__(self, lock: Lock, rel_path: str):
        self.lock = lock
        self.rel_path = rel_path
        self.envvars: dict[str, str] = {}

    def __str__(self):
        return f"ToolRequest(lock={self.lock}, rel_path={self.rel_path})"
    
    def inject_envvar(self, key: str, value: str) -> 'WasmToolRequest':
        self.envvars[key] = value
        return self

def from_local(path: str) -> WasmToolRequest:
    return WasmToolRequest(LocalLock(path), "")


def from_git(repository: str, ref: str, rel_path: str) -> WasmToolRequest:
    return WasmToolRequest(GitLock(repository_url=repository, git_ref=ref), rel_path)


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
        
        app_settings_path = pathlib.Path(os.getcwd()) / "settings.toml"

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
            
        tool_envvars = cls._get_envvars_from_config(config)
        if tool_envvars:
            tool_envvars = cls._inject_envvar(app_settings_path, tool_envvars, tool_req)

            # write tool_envvars to config.toml envvar
            config['envvar'] = tool_envvars
            with config_path.open("w") as f:
                toml.dump(config, f)

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
    def _get_envvars_from_config(cls, config: dict) -> dict:
        tool_envvars = config.get("envvar")
        if not tool_envvars:
            return 
        tool_envvars_dict = {}
        for key, value in tool_envvars.items():
            tool_envvars_dict[key] = value
        return tool_envvars_dict
    
    @classmethod
    def _get_envvars_from_settings(cls, settings_path: pathlib.Path) -> dict:
        with settings_path.open("r") as f:
            settings = toml.load(f)
            app_envvars = settings.get("envvar")
            if not app_envvars:
                return
            app_envvars_dict = {}
            for key, value in app_envvars.items():
                app_envvars_dict[key] = value
            return app_envvars_dict
    
    @classmethod
    def _inject_envvar(cls, settings_path:pathlib.Path, tool_envvars: dict, tool_req: WasmToolRequest) -> dict:
        not_found_envvars = []
            
        # envvars set from application code
        for k in tool_envvars.keys():
            if k in tool_req.envvars:
                tool_envvars[k] = tool_req.envvars[k]
            else:
                not_found_envvars.append(k)
        
        # envvars set from settings.toml in application code
        if settings_path.exists():
            app_envvars = cls._get_envvars_from_settings(settings_path)
            if app_envvars:
                for k in not_found_envvars:
                    if k in app_envvars:
                        tool_envvars[k] = app_envvars[k]
                        not_found_envvars.remove(k)
                            
        # require users to provide not_found_envvars from prompt
        for k in not_found_envvars:
            print(f"The following environment variables {k} are not found in the current environment:")
            print("Please add the following environment variables to the current environment:")
            user_input = input(f"{k}: ")
            if user_input:
                tool_envvars[k] = user_input

        return tool_envvars
    
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
