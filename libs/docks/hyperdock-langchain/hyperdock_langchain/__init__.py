from typing import Callable

from hyperdock_langchain.connector import LangchainToolRequest, connect
from hyperdock_langchain.dictionary import Converter, EnvDict


def dock(
    *requests: list[LangchainToolRequest],
) -> list[Callable[[...], str]]:
    return [connect(request) for request in requests]


__all__ = ["dock", "connect", "LangchainToolRequest", "Converter", "EnvDict"]
