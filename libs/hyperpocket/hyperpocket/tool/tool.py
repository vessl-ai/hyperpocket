import abc
from typing import Callable, Optional, Type

from pydantic import BaseModel, Field

from hyperpocket.auth.provider import AuthProvider
from hyperpocket.config.logger import pocket_logger
from hyperpocket.prompts import pocket_extended_tool_description
from hyperpocket.util.json_schema_to_model import json_schema_to_model


class ToolAuth(BaseModel):
    """
    ToolAuth is an object that represents the authentication information required to invoke a tool
    """

    scopes: list[str] = Field(
        default=None,
        description="Indicates which authentication provider’s credentials are required to invoke the tool. "
                    "If auth_provider is not specified, the tool is considered to require no authentication.",
    )
    auth_provider: Optional[AuthProvider] = Field(
        default=None,
        description="Specifies which authentication handler should be used when invoking the tool. "
                    "If auth_handler is not specified, the default handler of the authentication provider will be used.",
    )
    auth_handler: Optional[str] = Field(
        default=None,
        description="Indicates the authentication scopes required to invoke the tool. "
                    "If authentication is not performed or the authentication handler is non-scoped, the value should be None.",
    )


class Tool(BaseModel, abc.ABC):
    """
    Pocket Tool Interface
    """

    name: str = Field(description="tool name")
    description: str = Field(description="tool description")
    argument_json_schema: Optional[dict] = Field(
        default=None, description="tool argument json schema"
    )
    auth: Optional[ToolAuth] = Field(
        default=None, description="authentication information to invoke tool"
    )
    postprocessings: Optional[list[Callable]] = Field(
        default=None, description="postprocessing functions after tool is invoked"
    )
    default_tool_vars: dict[str, str] = Field(
        default_factory=dict, description="default tool variables"
    )
    overridden_tool_vars: dict[str, str] = Field(
        default_factory=dict, description="overridden tool variables"
    )
    use_profile: bool = False

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

    def schema_model(self, use_profile: bool = False) -> Optional[Type[BaseModel]]:
        """
        Returns a schema_model that wraps the existing argument_json_schema
        to include profile and thread_id as arguments when the tool is invoked
        """
        return self._get_schema_model(
            self.name, self.argument_json_schema, use_profile=use_profile
        )

    def get_description(self, use_profile: bool = False) -> str:
        if use_profile:
            return pocket_extended_tool_description(self.description)
        else:
            return self.description

    def override_tool_variables(self, override_vars: dict[str, str]) -> "Tool":
        self.overridden_tool_vars |= override_vars
        return self

    @property
    def tool_vars(self) -> dict[str, str]:
        return self.default_tool_vars | self.overridden_tool_vars

    @classmethod
    def _get_schema_model(
        cls, name: str, json_schema: Optional[dict], use_profile: bool
    ) -> Optional[Type[BaseModel]]:
        try:
            if not json_schema:
                pocket_logger.info(f"{name} tool's json_schema is none.")
                return None
            if "description" not in json_schema:
                json_schema["description"] = "The argument of the tool."

            if use_profile:
                json_schema = {
                    "title": name,
                    "type": "object",
                    "properties": {
                        "thread_id": {
                            "type": "string",
                            "default": "default",
                            "description": "The ID of the chat thread where the tool is invoked. Omitted when unknown.",
                        },
                        "profile": {
                            "type": "string",
                            "default": "default",
                            "description": """The profile of the user invoking the tool. Inferred from user's messages.
                            Users can request tools to be invoked in specific personas, which is called a profile.
                            If the user's profile name can be inferred from the query, pass it as a string in the 'profile'
                            JSON property. Omitted when unknown.""",
                        },
                        "body": json_schema,
                    },
                    "required": [
                        "body",
                    ],
                }

            model = json_schema_to_model(json_schema, name)
            return model
        except Exception as e:
            pocket_logger.warning(
                f"failed to get tool({name}) schema model. error : {e}"
            )
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

    def __str__(self) -> str:
        return self.name
