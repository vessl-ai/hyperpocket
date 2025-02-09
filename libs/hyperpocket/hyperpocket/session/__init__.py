from hyperpocket.session.interface import SessionStorageInterface
from hyperpocket.util.find_all_leaf_class_in_package import (
    find_all_leaf_class_in_package,
)

SESSION_STORAGE_LIST = find_all_leaf_class_in_package(
    "hyperpocket.session", SessionStorageInterface
)
