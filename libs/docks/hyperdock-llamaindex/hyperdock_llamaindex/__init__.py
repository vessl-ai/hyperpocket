from typing import Callable

from hyperdock_llamaindex.connector import LlamaIndexToolRequest, connect


def dock(
    *requests: list[LlamaIndexToolRequest],
) -> list[Callable[[...], str]]:
    return [connect(request) for request in requests]


__all__ = ["dock", "connect", "LlamaIndexToolRequest"]
