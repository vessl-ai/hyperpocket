import abc
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Coroutine, Any

from fastapi import APIRouter

from hyperpocket.repository import Lock, LockSection, SerializedLockSection
from hyperpocket.tool import ToolRequest
from hyperpocket.tool.function import FunctionTool

CallbackExtends = Callable[..., Coroutine[Any, Any, Any]]

class Dock(abc.ABC):
    _identifier: str
    _locks: dict[str, Lock]
    _tool_requests: list[ToolRequest]
    _dock_vars: dict[str, str]
    
    def __init__(self, identifier: str, dock_vars: dict[str, str] = None):
        self._identifier = identifier
        self._dock_http_router = APIRouter()
        self._tool_requests = []
        self._locks = dict()
        self._dock_vars = dock_vars if dock_vars is not None else {}
    
    @property
    def identifier(self):
        return self._identifier
    
    def dock_http_router(self) -> APIRouter:
        return self._dock_http_router
    
    def locks(self) -> dict[str, Lock]:
        return self._locks
    
    def sync(self, parallel=True, **kwargs):
        if parallel:
            with ThreadPoolExecutor(
                max_workers=min(len(self._locks) + 1, 100), thread_name_prefix="repository_loader"
            ) as executor:
                executor.map(lambda k: self._locks[k].sync(**kwargs), self._locks.keys())
        else:
            for key in self._locks.keys():
                self._locks[key].sync(**kwargs)

    def load_lock_section(self, serialized_lock_section: SerializedLockSection):
        for key, lock in serialized_lock_section.items():
            self._locks[key] = self.deserialize_lock(key, lock)

    @abc.abstractmethod
    def deserialize_lock(self, lock_key: str, serialized_lock: dict) -> Lock:
        raise NotImplementedError

    @abc.abstractmethod
    def plug(self, **kwargs):
        raise NotImplementedError
    
    @abc.abstractmethod
    def tools(self) -> list[FunctionTool]:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def teardown(self):
        raise NotImplementedError
