import abc
import json
import pathlib
from typing import Optional, Any

from hyperpocket.auth import AuthProvider
from hyperpocket.tool import ToolAuth
from hyperpocket.tool.function import FunctionTool
from hyperpocket.util.generate_slug import generate_slug

from hyperdock_container.settings import settings, Runtime
from hyperdock_container.tool import ContainerToolRequest


class ToolContainer(object):
    runtime: "ContainerRuntime"
    base_image_tag: str
    commit: bool
    tool_image_tag: Optional[str]
    container_args: dict
    cmd: str
    envs: dict

    def __init__(self,
                 runtime: "ContainerRuntime",
                 image_tag: str,
                 cmd: str,
                 envs: dict,
                 commit: bool = False,
                 tool_image_tag: Optional[str] = None, **kwargs):
        self.runtime = runtime
        self.base_image_tag = image_tag
        self.commit = commit
        self.cmd = cmd
        self.envs = envs
        if commit:
            if tool_image_tag is None:
                raise ValueError("tool_image_tag is required when commit is True")
            self.tool_image_tag = tool_image_tag
        self.container_args = kwargs

    def __enter__(self):
        try:
            self.container_id = self.runtime.create(
                self.base_image_tag, "/tool", self.cmd, self.envs, **self.container_args)
            return self.container_id
        except Exception as e:
            import traceback
            traceback.print_exc()
            traceback.print_stack()
            raise e

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.runtime.stop(self.container_id)
        except Exception:
            pass
        try:
            if self.commit and exc_type is None:
                self.runtime.commit(self.container_id, "hyperpocket", self.tool_image_tag)
            self.runtime.remove(self.container_id)
        except Exception:
            pass


class ContainerRuntime(abc.ABC):
    @abc.abstractmethod
    def create(self, image_tag: str, workdir: str, command: str, envs: dict, **kwargs) -> str:
        """
        Create an image from tag
        :param image_tag: 
        :param workdir:
        :param command:
        :param envs:
        :return: container id
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def start(self, container_id: str) -> None:
        """
        Start a container
        :param container_id: 
        :return: 
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def stop(self, container_id: str) -> None:
        """
        Stop a container
        :param container_id: 
        :return: 
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def remove(self, container_id: str) -> None:
        """
        Remove a container
        :param container_id: 
        :return: 
        """
        raise NotImplementedError

    @abc.abstractmethod
    def pull(self, image_tag: str) -> str:
        """
        Pull an image from tag and returns its id
        :param image: 
        :return: 
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def list_image(self) -> list[tuple[str, list[str]]]:
        """
        List all images
        :return: list of image id and tag list
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def run(self, container_id: str, stdin_str: Optional[str] = None) -> str:
        """
        Run a command in a container
        :param container_id:
        :param stdin_str: 
        :return: stdout_str of container
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def put_archive(self, container_id: str, source: pathlib.Path, dest: str) -> None:
        """
        Put an archive to a container
        :param container_id: 
        :param source: 
        :param dest: 
        :return: 
        """
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self, container_id: str, repository: str, tag: str) -> str:
        """
        Commit a container to an image
        :param container_id: 
        :param repository:
        :param tag: 
        :return: image id
        """
        raise NotImplementedError
    
    def from_single_tool_config(
            self,
            tool_image_tag: str,
            pocket_tool_config_path: pathlib.Path,
            overridden_tool_vars: dict[str, str] = None,
            runtime_arguments: dict = None) -> FunctionTool:
        if runtime_arguments is None:
            runtime_arguments = dict()
        
        with pocket_tool_config_path.open("r") as f:
            pocket_tool_config = json.load(f)
        
        # 1. tool section
        mcp_tool_config = pocket_tool_config["tool"]
        name = mcp_tool_config["name"]
        description = mcp_tool_config.get("description", "")
        json_schema = mcp_tool_config.get("inputSchema", {})

        # 2. variable section
        default_tool_vars = pocket_tool_config.get("variables", {})

        # 3. auth section
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
            
        if pocket_tool_config.get("entrypoint", {}).get("run") is None:
            raise ValueError("entrypoint.run is required in pocket tool configuration")
        
        run_command = pocket_tool_config["entrypoint"]["run"]

        tool_image = f"hyperpocket:{tool_image_tag}"
        def _invoke(body: Any, envs: dict, **kwargs) -> str:
            print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            with ToolContainer(
                self,
                tool_image,
                cmd=run_command,
                envs=envs,
                commit=False,
                stdin_open=True,
                **runtime_arguments) as tool_container_id:
                return self.run(tool_container_id, stdin_str=json.dumps(body))

        async def _ainvoke(body: Any, envs: dict, **kwargs) -> str:
            return _invoke(body, envs, **kwargs)

        model = json_schema
        _ainvoke.__name__ = name
        _ainvoke.__doc__ = description
        _ainvoke.__model__ = model
        _invoke.__name__ = name
        _invoke.__doc__ = description
        _invoke.__model__ = model

        tool = FunctionTool.from_func(
            func=_invoke,
            afunc=_ainvoke,
            auth=auth,
            tool_vars=default_tool_vars,
            keep_structured_arguments=True,
        )
        if overridden_tool_vars is not None:
            tool.override_tool_variables(overridden_tool_vars)
        return tool
    
    def from_tool_request(self, tool_request: ContainerToolRequest) -> list[FunctionTool]:
        """
        Create a FunctionTool from a tool request
        :param tool_request: 
        :return: 
        """
        toolpkg_path = tool_request.tool_ref.toolpkg_path()
        rel_path = tool_request.rel_path
        rootpath = pathlib.Path(toolpkg_path) / rel_path
        pocket_tool_config_path = rootpath / "pocket.json"
        
        with pocket_tool_config_path.open("r") as f:
            pocket_tool_config = json.load(f)

        # 4. entrypoint section
        entrypoint = pocket_tool_config["entrypoint"]
        build_cmd = entrypoint.get("build")
        
        tool_image_tag = generate_slug()
        with ToolContainer(
            self,
            tool_request.base_image,
            cmd = build_cmd if build_cmd is not None else "true",
            envs = dict(),
            commit=True,
            tool_image_tag=tool_image_tag,
            **tool_request.runtime_arguments) as container_id:
            self.put_archive(container_id, toolpkg_path, "/tool")
            if build_cmd is not None:
                self.run(container_id)

        tools = []
        if pocket_tool_config.get("include") is not None:
            include = pocket_tool_config["include"]
            for inc in include:
                inc_path = rootpath / inc
                tools.append(self.from_single_tool_config(tool_image_tag, inc_path))
        else:
            tools = [self.from_single_tool_config(tool_image_tag, pocket_tool_config_path)]
        return tools
    
    @classmethod
    def get_runtime_from_settings(cls) -> "ContainerRuntime":
        from hyperdock_container.runtime.docker.runtime_docker import DockerContainerRuntime
        if settings().runtime == Runtime.DOCKER:
            return DockerContainerRuntime(settings().docker)
        raise ValueError(f"Unsupported runtime: {settings().runtime}")
        