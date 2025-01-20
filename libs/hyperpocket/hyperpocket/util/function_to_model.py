import inspect
from inspect import signature, Parameter
from typing import Any, Dict, Type, Tuple

from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from hyperpocket.config import pocket_logger
from hyperpocket.util.extract_func_param_desc_from_docstring import extract_param_docstring_mapping


def function_to_model(func: callable) -> Type[BaseModel]:
    docstring = inspect.getdoc(func)
    if docstring is None:
        pocket_logger.info("not found docstring. use function name as description instead.")
        docstring = func.__name__
    fields: Dict[str, Tuple[Type, Any]] = {}
    sig = signature(func)
    param_desc_map = extract_param_docstring_mapping(func)

    for param_name, param in sig.parameters.items():
        if param_name in ('self', 'cls'):
            continue

        if param.kind == Parameter.VAR_POSITIONAL:
            # don't support var positional args
            continue

        elif param.kind == Parameter.VAR_KEYWORD:
            fields[param_name] = (Dict[str, Any], {})
            continue

        if param.annotation is Parameter.empty:
            raise Exception(f"Should all arguments be annotated but {param_name} is not annotated")

        if param.annotation.__module__ == "typing" and param.annotation.__name__ == "Optional":
            fields[param_name] = (
                param.annotation.__args__[0], FieldInfo(default=param.default, description=param_desc_map.get(param_name, "")))
        elif param.annotation.__module__ != "builtins" and not issubclass(param.annotation, BaseModel):
            raise Exception(
                f"currently only support builtin types and pydantic BaseModel but {param_name} is not builtin type")

        default = param.default if param.default is not Parameter.empty else ...

        fields[param_name] = (
            param.annotation, FieldInfo(default=default, description=param_desc_map.get(param_name, "")))

    model = create_model(f"{func.__name__.capitalize()}Model", **fields, __doc__=docstring)
    return model
