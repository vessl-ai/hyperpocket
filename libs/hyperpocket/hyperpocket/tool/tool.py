import abc
from typing import Optional, Type

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
    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError


class Tool(BaseModel, abc.ABC):
    """
    Pocket Tool Interface
    """
    name: str = Field(description="tool name")
    description: str = Field(description="tool description")
    argument_json_schema: Optional[dict] = Field(default=None, description="tool argument json schema")
    auth: Optional[ToolAuth] = Field(default=None, description="authentication information to invoke tool")

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
