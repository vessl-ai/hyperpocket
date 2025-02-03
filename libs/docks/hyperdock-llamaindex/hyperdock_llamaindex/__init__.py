from typing import Callable

from hyperdock_llamaindex.connector import LlamaIndexToolRequest, connect
from hyperdock_llamaindex.dictionary import Converter, EnvDict


def dock(
    *requests: list[LlamaIndexToolRequest],
) -> list[Callable[[...], str]]:
    return [connect(request) for request in requests]


__all__ = ["dock", "connect", "LlamaIndexToolRequest", "Converter", "EnvDict"]
