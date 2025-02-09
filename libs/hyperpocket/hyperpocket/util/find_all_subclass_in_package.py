import importlib
import inspect
import pkgutil
from typing import List, Type, TypeVar

from hyperpocket.config import pocket_logger

T = TypeVar("T")


def find_all_subclass_in_package(package_name: str, interface_type: Type[T]) -> List[T]:
    subclasses = set()
    package = importlib.import_module(package_name)

    for _, module_name, is_pkg in pkgutil.walk_packages(
        package.__path__, package.__name__ + "."
    ):
        try:
            if "tests" in module_name or is_pkg:
                continue

            module = importlib.import_module(module_name)
            module_classes = inspect.getmembers(module, inspect.isclass)
            for _, obj in module_classes:
                if issubclass(obj, interface_type) and obj is not interface_type:
                    subclasses.add(obj)
        except ImportError as e:
            pocket_logger.warning(f"failed to import {module_name}. error : {e}")
            continue

    return list(subclasses)
