import abc
from typing import Any

from fastapi import APIRouter

from hyperpocket.tool import ToolRequest
from hyperpocket.tool.function import FunctionTool


class Dock(abc.ABC):
    _tool_requests: list[ToolRequest]
    _dock_http_router: APIRouter
    _dock_vars: dict[str, str]

    def __init__(self, dock_vars: dict[str, str] = None):
        self._dock_http_router = APIRouter()
        self._tool_requests = []
        self._dock_vars = dock_vars if dock_vars is not None else {}

    @property
    def router(self):
        return self._dock_http_router

    @abc.abstractmethod
    def plug(self, req_like: Any, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def tools(self) -> list[FunctionTool]:
        raise NotImplementedError

    @abc.abstractmethod
    async def teardown(self):
        raise NotImplementedError
