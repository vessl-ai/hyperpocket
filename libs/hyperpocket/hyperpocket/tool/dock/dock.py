import abc
from typing import TypeVar, Generic

from hyperpocket.tool.function import FunctionTool

DockToolLike = TypeVar("DockToolLike")


class Dock(Generic[DockToolLike], abc.ABC):
    @abc.abstractmethod
    def dock(self, tool_like: DockToolLike, *args, **kwargs) -> FunctionTool:
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.dock(*args, **kwargs)
