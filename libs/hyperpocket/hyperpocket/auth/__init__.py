from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.provider import AuthProvider
from hyperpocket.util.find_all_leaf_class_in_package import (
    find_all_leaf_class_in_package,
)

PREBUILT_AUTH_HANDLERS = find_all_leaf_class_in_package(
    "hyperpocket.auth", AuthHandlerInterface
)
AUTH_CONTEXT_MAP = {
    leaf.__name__: leaf
    for leaf in find_all_leaf_class_in_package("hyperpocket.auth", AuthContext)
}

__all__ = [
    "PREBUILT_AUTH_HANDLERS",
    "AUTH_CONTEXT_MAP",
    "AuthProvider",
    "AuthHandlerInterface",
]
