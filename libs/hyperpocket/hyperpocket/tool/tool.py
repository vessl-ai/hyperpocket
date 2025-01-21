import abc
import pathlib

import toml
from typing import Optional, Type, Callable

from pydantic import BaseModel, Field

from hyperpocket.auth.provider import AuthProvider
from hyperpocket.config.logger import pocket_logger
from hyperpocket.util.json_schema_to_model import json_schema_to_model


class ToolAuth(BaseModel):
    """
    ToolAuth is an object that represents the authentication information required to invoke a tool
    """
    scopes: list[str] = Field(
        default=None,
        description="Indicates which authentication provider’s credentials are required to invoke the tool. "
                    "If auth_provider is not specified, the tool is considered to require no authentication.")
    auth_provider: Optional[AuthProvider] = Field(
        default=None,
        description="Specifies which authentication handler should be used when invoking the tool. "
                    "If auth_handler is not specified, the default handler of the authentication provider will be used.")
    auth_handler: Optional[str] = Field(
        default=None,
        description="Indicates the authentication scopes required to invoke the tool. "
                    "If authentication is not performed or the authentication handler is non-scoped, the value should be None.")


class ToolRequest(abc.ABC):
    postprocessings: Optional[list[Callable]] = None
    tool_var: dict[str, str] = {}

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError
    
    def add_postprocessing(self, postprocessing: Callable):
        if self.postprocessings is None:
            self.postprocessings = [postprocessing]
        else:
            self.postprocessings.append(postprocessing)
    
    def add_tool_var(self, tool_var: dict) -> 'ToolRequest':
        self.tool_var = tool_var
        return self

    def __or__(self, other: Callable):
        self.add_postprocessing(other)
        return self

    def with_postprocessings(self, postprocessings: list[Callable]):
        if self.postprocessings is None:
            self.postprocessings = postprocessings
        else:
            self.postprocessings.extend(postprocessings)
        return self


class Tool(BaseModel, abc.ABC):
    """
    Pocket Tool Interface
    """
    name: str = Field(description="tool name")
    description: str = Field(description="tool description")
    argument_json_schema: Optional[dict] = Field(default=None, description="tool argument json schema")
    auth: Optional[ToolAuth] = Field(default=None, description="authentication information to invoke tool")
    postprocessings: Optional[list[Callable]] = Field(default=None, description="postprocessing functions after tool is invoked")
    tool_var: dict[str, str] = {}

    @abc.abstractmethod
    def invoke(self, **kwargs) -> str:
        """
        Invoke the tool
        """
        raise NotImplementedError()

    async def ainvoke(self, **kwargs) -> str:
        """
        Asynchronously invoke the tool
        """
        raise NotImplementedError()

    def schema_model(self) -> Optional[Type[BaseModel]]:
        """
        Returns a schema_model that wraps the existing argument_json_schema
        to include profile and thread_id as arguments when the tool is invoked
        """
        return self._get_schema_model(self.name, self.argument_json_schema)
    
    @classmethod
    def add_tool_var(cls, tool_var: dict) -> 'Tool':
        cls.tool_var = tool_var
        return cls
    
    @classmethod
    def inject_tool_var(cls, settings_path: pathlib.Path, tool_vars: dict, app_tool_vars: dict) -> dict:
        not_found_tool_vars = []
            
        # tool_vars set from application code
        for k in tool_vars.keys():
            if k in app_tool_vars:
                tool_vars[k] = app_tool_vars[k]
            else:
                not_found_tool_vars.append(k)
        
        # tool_vars set from settings.toml in application code
        if settings_path.exists():
            app_tool_vars = cls._get_tool_vars_from_settings(settings_path)
            if app_tool_vars:
                for k in not_found_tool_vars:
                    if k in app_tool_vars:
                        tool_vars[k] = app_tool_vars[k]
                        not_found_tool_vars.remove(k)
                            
        # require users to provide not_found_tool_vars from prompt
        for k in not_found_tool_vars:
            print(f"The following tool variables {k} are not found in the current environment:")
            print("Please add the following tool variables to the current environment:")
            user_input = input(f"{k}: ")
            if user_input:
                tool_vars[k] = user_input

        return tool_vars
    
    @classmethod
    def _get_tool_vars_from_settings(cls, settings_path: pathlib.Path) -> dict:
        with settings_path.open("r") as f:
            settings = toml.load(f)
            app_tool_vars = settings.get("tool_var")
            if not app_tool_vars:
                return
            app_tool_vars_dict = {}
            for key, value in app_tool_vars.items():
                app_tool_vars_dict[key] = value
            return app_tool_vars_dict

    @classmethod
    def from_tool_request(cls, tool_req: ToolRequest, **kwargs) -> 'Tool':
        from hyperpocket.tool.wasm.tool import WasmTool, WasmToolRequest
        if isinstance(tool_req, WasmToolRequest):
            return WasmTool.from_tool_request(tool_req, **kwargs)
        raise ValueError('Unknown tool request type')

    @classmethod
    def _get_schema_model(cls, name: str, json_schema: Optional[dict]) -> Optional[Type[BaseModel]]:
        try:
            if not json_schema:
                pocket_logger.info(f"{name} tool's json_schema is none.")
                return None
            if 'description' not in json_schema:
                json_schema['description'] = 'The argument of the tool.'
            extended_schema = {
                'title': name,
                'type': 'object',
                'properties': {
                    'thread_id': {
                        'type': 'string',
                        'default': 'default',
                        'description': 'The ID of the chat thread where the tool is invoked. Omitted when unknown.',
                    },
                    'profile': {
                        'type': 'string',
                        'default': 'default',
                        'description': '''The profile of the user invoking the tool. Inferred from user's messages.
                        Users can request tools to be invoked in specific personas, which is called a profile.
                        If the user's profile name can be inferred from the query, pass it as a string in the 'profile'
                        JSON property. Omitted when unknown.''',
                    },
                    'body': json_schema
                },
                'required': [
                    'body',
                ]
            }
            model = json_schema_to_model(extended_schema, name)
            return model
        except Exception as e:
            pocket_logger.warning(f"failed to get tool({name}) schema model. error : {e}")
            pass

    def with_postprocessing(self, postprocessing: Callable):
        """
        Add a postprocessing function to the tool
        """
        if self.postprocessings is None:
            self.postprocessings = [postprocessing]
        else:
            self.postprocessings.append(postprocessing)
        return self

    def __or__(self, other: Callable):
        self.with_postprocessing(other)
        return self

    def with_postprocessings(self, postprocessings: list[Callable]):
        """
        Add a list of postprocessing functions to the tool
        Returns the tool itself
        """
        if self.postprocessings is None:
            self.postprocessings = postprocessings
        else:
            self.postprocessings.extend(postprocessings)
        return self
