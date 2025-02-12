import abc
import string, random
from typing import Callable, Coroutine, Any

from fastapi import APIRouter

from hyperpocket.tool import ToolRequest
from hyperpocket.tool.function import FunctionTool
from hyperpocket.util.generate_slug import generate_slug

CallbackExtends = Callable[..., Coroutine[Any, Any, Any]]

class Dock(abc.ABC):
    _identifier: str
    _tool_requests: list[ToolRequest]
    _dock_http_router: APIRouter
    _dock_vars: dict[str, str]
    
    def __init__(self, identifier: str, dock_vars: dict[str, str] = None):
        self._identifier = identifier
        dock_slug = generate_slug()
        self._unique_identifier = f"{identifier}-{dock_slug}"
        self._dock_http_router = APIRouter(prefix=f"/{self._unique_identifier}")
        self._tool_requests = []
        self._locks = dict()
        self._dock_vars = dock_vars if dock_vars is not None else {}
    
    @property
    def router(self):
        return self._dock_http_router
    
    @property
    def identifier(self):
        return self._identifier
    
    @property
    def unique_identifier(self):
        return self._unique_identifier
    
    def dock_http_router(self) -> APIRouter:
        return self._dock_http_router

    @abc.abstractmethod
    def plug(self, req_like=Any, **kwargs):
        raise NotImplementedError
    
    @abc.abstractmethod
    def tools(self) -> list[FunctionTool]:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def teardown(self):
        raise NotImplementedError
