import abc
import pathlib

from pydantic import BaseModel


class ToolReference(BaseModel, abc.ABC):
    tool_source: str = None

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def key(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def sync(self, **kwargs):
        raise NotImplementedError

    def eject_to_path(self, dest_path: pathlib.Path, src_sub_path: str = None):
        ## local locks are already tracked by git
        raise NotImplementedError




