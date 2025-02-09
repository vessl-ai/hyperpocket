import importlib
import pkgutil
from typing import Optional, Type


def get_objects_from_subpackage(package_name, interface_type: Optional[Type] = None):
    """
    Retrieves objects from a specific subpackage.

    Args:
        package_name (str): The name of the package to search (e.g., "mypackage.subpackage").
        interface_type (Optional[Type]): A type to filter objects. Defaults to None (returns all objects).
    Returns:
        list: A list of objects matching the interface_type
    """
    objects = []

    package = importlib.import_module(package_name)
    package_path = package.__path__

    for module_info in pkgutil.walk_packages(package_path, package_name + "."):
        module = importlib.import_module(module_info.name)

        for name, obj in vars(module).items():
            if interface_type is None or isinstance(obj, interface_type):
                objects.append(obj)

    return objects
