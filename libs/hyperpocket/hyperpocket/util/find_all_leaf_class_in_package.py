from typing import List, Type, TypeVar

from hyperpocket.util.find_all_subclass_in_package import find_all_subclass_in_package

T = TypeVar("T")


def find_all_leaf_class_in_package(
    package_name: str, interface_type: Type[T]
) -> List[T]:
    parent_class_set = set()
    subclasses = find_all_subclass_in_package(package_name, interface_type)

    for sub in subclasses:
        parent_class_set.add(*sub.__bases__)

    leaf_sub_classes = [sub for sub in subclasses if sub not in parent_class_set]
    return leaf_sub_classes
