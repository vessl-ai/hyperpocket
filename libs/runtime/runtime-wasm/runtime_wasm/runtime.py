import abc


class WasmRuntime(abc.ABC):
    @classmethod
    @abc.abstractmethod
    async def ainvoke(cls, *args, **kwargs):
        raise NotImplementedError
