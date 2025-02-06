from typing import Callable

from hyperdock_llamaindex.connector import LlamaIndexToolRequest, connect


def dock(
    *requests: list[LlamaIndexToolRequest],
) -> list[Callable[[...], str]]:
    result = []
    for request in requests:
        for tool_func in request.tool_func:
            request_copy = request
            request_copy.tool_func = tool_func
            result.append(connect(request_copy))
    return result


__all__ = ["dock", "connect", "LlamaIndexToolRequest"]
