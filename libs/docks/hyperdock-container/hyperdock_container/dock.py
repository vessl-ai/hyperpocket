import json
import pathlib
from typing import Any, Union
from urllib.parse import urlparse

import git
from pydantic import BaseModel
from typing_extensions import override

from hyperdock_container.runtime import ContainerRuntime
from hyperpocket.auth import AuthProvider
from hyperpocket.config import pocket_logger, settings
from hyperpocket.tool import ToolAuth
from hyperpocket.tool.dock import Dock
from hyperpocket.tool.function import FunctionTool
from hyperpocket.util.git_parser import GitParser
from hyperpocket.util.short_hashing_str import short_hashing_str

ContainerToolLike = Union[str, tuple]


class DockArguments(BaseModel):
    request_tool_path: str
    tool_path: pathlib.Path
    tool_vars: dict
    runtime_arguments: dict
    tool_source: str
    image_tag_postfix: str


class ContainerDock(Dock[ContainerToolLike]):
    runtime: ContainerRuntime = ContainerRuntime.get_runtime_from_settings()

    @override
    def dock(self, tool_like: ContainerToolLike, dock_vars: dict[str, str] = None,
             runtime_arguments: dict = None, *args, **kwargs) -> FunctionTool:
        dock_args = self.load(tool_like, dock_vars=dock_vars, runtime_arguments=runtime_arguments, *args, **kwargs)
        self.build(dock_args, *args, **kwargs)
        return self._dock(dock_args, *args, **kwargs)

    def load(self, tool_like: ContainerToolLike, dock_vars: dict = None, runtime_arguments: dict = None, *args,
             **kwargs) -> DockArguments:
        pocket_logger.info(f"start loading source... {tool_like}")

        if dock_vars is None:
            dock_vars = {}
        if runtime_arguments is None:
            runtime_arguments = {}

        if not isinstance(tool_like, ContainerToolLike):
            raise AttributeError(f"not supported container tool_like: {tool_like}")

        if isinstance(tool_like, tuple) and len(tool_like) == 2:
            req_path, inline_tool_vars = tool_like
        elif isinstance(tool_like, str):
            req_path, inline_tool_vars = tool_like, dict()
        else:
            raise AttributeError(f"not supported container tool_like: {tool_like}")

        tool_path = None
        tool_source = None
        image_tag_postfix = None
        # sources: local
        if pathlib.Path(req_path).expanduser().exists():
            tool_source = "local"
            tool_path = pathlib.Path(req_path).expanduser().resolve()
            image_tag_postfix = short_hashing_str(f"{str(tool_path)}-none")

        # sources: github
        elif req_path.startswith("https://github.com"):
            tool_source = "github"
            base_repo, branch_name, directory_path, git_sha = GitParser.parse_repo_url(req_path)
            cleaned_base_repo = base_repo[8:]
            last_directory_name = directory_path.split("/")[-1]  # usually tool name
            base_tool_path = settings.toolpkg_path / last_directory_name / cleaned_base_repo / git_sha
            tool_path = base_tool_path / directory_path
            image_tag_postfix = short_hashing_str(f"{self.normalize_url(req_path)}-{git_sha}")

            # NOTE(moon): supporting overwriting it?
            if tool_path.expanduser().exists():
                pocket_logger.debug(
                    f"skip git pull. tool directory already exists in {tool_path.expanduser().resolve()}")
            else:
                repo = git.Repo.clone_from(
                    base_repo,
                    base_tool_path,
                    branch=branch_name,
                    depth=1,
                    no_checkout=True,
                    filter="blob:none"
                )

                if directory_path:
                    repo.git.sparse_checkout("init", "--no-cone")
                    repo.git.sparse_checkout("set", directory_path)
                repo.git.checkout()
        else:
            raise RuntimeError(f"not supported container tool_like {tool_like}")

        pocket_logger.info(f"end loading source. tool_path: {str(tool_path)}")
        return DockArguments(
            tool_path=tool_path,
            tool_source=tool_source,
            request_tool_path=req_path,
            tool_vars=dock_vars | inline_tool_vars,
            runtime_arguments=runtime_arguments,
            image_tag_postfix=image_tag_postfix
        )

    def build(self, dock_args: DockArguments, *args, **kwargs) -> str:
        pocket_logger.info(f"start building container dock... {dock_args.request_tool_path}")

        with (dock_args.tool_path / "pocket.json").open("r") as f:
            pocket_config = json.load(f)

        tool_name = pocket_config["tool"]["name"]
        entrypoint = pocket_config["entrypoint"]
        build_cmd = entrypoint.get("build")
        base_image = self.get_base_image(pocket_config)
        image_tag = f"{tool_name}-{dock_args.image_tag_postfix}"

        if not self.runtime.list_image(name=base_image):
            pocket_logger.debug(f"base image({base_image}) doesn't exist. pull {base_image}.")
            self.runtime.pull(base_image)

        if self.runtime.list_image(name=f"hyperpocket:{image_tag}"):
            pocket_logger.debug("built image already exists. skip build.")
            return f"hyperpocket:{image_tag}"

        container_id = self.runtime.create(
            base_image,
            workdir="/tool",
            command=build_cmd,
            envs=dict(),
            **dock_args.runtime_arguments
        )

        try:
            self.runtime.put_archive(container_id, dock_args.tool_path, "/tool")
            if build_cmd is not None:
                self.runtime.run(container_id)
            self.runtime.commit(container_id, "hyperpocket", image_tag)
            return f"hyperpocket:{image_tag}"
        except Exception as e:
            raise e
        finally:
            self.runtime.stop(container_id)
            self.runtime.remove(container_id)
            pocket_logger.info(f"end building dock. {dock_args.request_tool_path}. image_tag: {image_tag}")

    def _dock(self, dock_args: DockArguments, *args, **kwargs):
        with (dock_args.tool_path / "pocket.json").open("r") as f:
            pocket_config = json.load(f)

        # 1. tool section
        tool_config = pocket_config["tool"]
        name = tool_config["name"]
        description = tool_config.get("description", "")
        json_schema = tool_config.get("inputSchema", {})
        image_tag = f"{name}-{dock_args.image_tag_postfix}"

        # 2. variable section
        default_tool_vars = pocket_config.get("variables", {})
        tool_vars = default_tool_vars | dock_args.tool_vars

        # 3. auth section
        auth = None
        if (_auth := pocket_config.get("auth")) is not None:
            auth_provider = _auth["auth_provider"]
            auth_handler = _auth.get("auth_handler")
            scopes = _auth.get("scopes", [])
            auth = ToolAuth(
                auth_provider=AuthProvider.get_auth_provider(auth_provider),
                auth_handler=auth_handler,
                scopes=scopes,
            )

        if pocket_config.get("entrypoint", {}).get("run") is None:
            raise ValueError("entrypoint.run is required in pocket tool configuration")

        run_command = pocket_config["entrypoint"]["run"]
        tool_image = f"hyperpocket:{image_tag}"

        def _invoke(body: Any, envs: dict, **kwargs) -> str:
            container_id = self.runtime.create(
                image_tag=tool_image,
                workdir="/tool",
                command=run_command,
                envs=envs,
                stdin_open=True,
                **dock_args.runtime_arguments
            )
            try:
                return self.runtime.run(container_id, stdin_str=json.dumps(body))
            finally:
                self.runtime.stop(container_id)
                self.runtime.remove(container_id)

        async def _ainvoke(body: Any, envs: dict, **kwargs) -> str:
            return _invoke(body, envs, **kwargs)

        tool = FunctionTool.from_func(
            func=_invoke,
            afunc=_ainvoke,
            auth=auth,
            name=name,
            description=description,
            json_schema=json_schema,
            tool_vars=tool_vars,
            keep_structured_arguments=True,
        )
        return tool

    @classmethod
    def get_base_image(cls, pocket_config: dict) -> str:
        if (base_image := pocket_config.get("baseImage")) is not None:
            return base_image

        if (language := pocket_config.get("language")) is not None:
            if lang := language.lower():
                if lang == "python":
                    return "python:3.11-slim"
                if lang == "node":
                    return "node"
        raise ValueError("failed to determine base image")

    @classmethod
    def normalize_url(cls, url):
        parsed = urlparse(url)

        base = parsed.netloc
        path = parsed.path
        if path is None:
            path = "/"

        return base + path
