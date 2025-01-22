import asyncio
import copy
import inspect
import pathlib
from typing import Any, Coroutine
from typing import Callable, Optional

import toml
from pydantic import BaseModel

from hyperpocket.tool.tool import Tool, ToolAuth
from hyperpocket.util.flatten_json_schema import flatten_json_schema
from hyperpocket.util.function_to_model import function_to_model


class FunctionTool(Tool):
    """
    FunctionTool is Tool executing local python method.
    """
    func: Optional[Callable[..., str]]
    afunc: Optional[Callable[..., Coroutine[Any, Any, str]]]

    def invoke(self, **kwargs) -> str:
        binding_args = self._get_binding_args(kwargs)
        if self.func is None:
            if self.afunc is None:
                raise ValueError("Both func and afunc are None")
            try:
                return str(asyncio.run(self.afunc(**binding_args)))
            except Exception as e:
                return "There was an error while executing the tool: " + str(e)
        try:
            return str(self.func(**binding_args))
        except Exception as e:
            return "There was an error while executing the tool: " + str(e)

    async def ainvoke(self, **kwargs) -> str:
        if self.afunc is None:
            return str(self.invoke(**kwargs))
        try:
            binding_args = self._get_binding_args(kwargs)
            return str(await self.afunc(**binding_args))
        except Exception as e:
            return "There was an error while executing the tool: " + str(e)

    def _get_binding_args(self, kwargs):
        _kwargs = copy.deepcopy(kwargs)

        # make body args to model
        schema_model = self.schema_model()
        model = schema_model(body=_kwargs["body"])
        _kwargs.pop("body")

        # body model to dict
        args = self.model_to_kwargs(model.body)

        # binding args
        binding_args = {}
        sig = inspect.signature(self.func)
        for param_name, param in sig.parameters.items():
            if param_name not in args:
                continue

            if param.kind == param.VAR_KEYWORD:
                # var keyword args should be passed by plain dict
                binding_args |= args[param_name]
                binding_args |= _kwargs.get("envs", {}) | self.tool_vars

                if "envs" in _kwargs:
                    _kwargs.pop("envs")

                binding_args |= _kwargs  # add other kwargs
                continue

            binding_args[param_name] = args[param_name]

        return binding_args

    @staticmethod
    def model_to_kwargs(model: BaseModel) -> dict:
        kwargs = {}
        for field, value in model.model_fields.items():
            attr_value = getattr(model, field)
            kwargs[field] = attr_value
        return kwargs

    @classmethod
    def from_func(
        cls,
        func: Callable | 'FunctionTool',
        afunc: Callable[..., Coroutine[Any, Any, str]] | 'FunctionTool' = None,
        auth: Optional[ToolAuth] = None,
        tool_vars: dict[str, str] = None,
    ) -> "FunctionTool":
        if tool_vars is None:
            tool_vars = dict()
            
        if isinstance(func, FunctionTool):
            if tool_vars is not None:
                func.override_tool_variables(tool_vars)
            return func
        elif isinstance(afunc, FunctionTool):
            if tool_vars is not None:
                afunc.override_tool_variables(tool_vars)
            return afunc
        elif not callable(func) and not callable(afunc):
            raise ValueError("FunctionTool can only be created from a callable")
        
        model = function_to_model(func)
        argument_json_schema = flatten_json_schema(model.model_json_schema())

        return cls(
            func=func,
            afunc=afunc,
            name=func.__name__,
            description=model.__doc__,
            argument_json_schema=argument_json_schema,
            auth=auth,
            default_tool_vars=tool_vars
        )
    
    @classmethod
    def from_dock(
        cls,
        dock: list[Callable[..., str]],
    ) -> list["FunctionTool"]:
        tools = []
        for func in dock:
            model = function_to_model(func)
            argument_json_schema = flatten_json_schema(model.model_json_schema())
            if not callable(func):
                raise ValueError(f"Dock element should be a list of functions, but found {func}")
            is_coroutine = inspect.iscoroutinefunction(func)
            auth = None
            if func.__dict__.get("__auth__") is not None:
                auth = ToolAuth(**func.__dict__["__auth__"])
            if is_coroutine:
                tools.append(cls(
                    func=None,
                    afunc=func,
                    name=func.__name__,
                    description=func.__doc__,
                    argument_json_schema=argument_json_schema,
                    auth=auth,
                ))
            else:
                tools.append(cls(
                    func=func,
                    afunc=None,
                    name=func.__name__,
                    description=func.__doc__,
                    argument_json_schema=argument_json_schema,
                    auth=auth,
                ))
        return tools
        
    @classmethod
    def _get_tool_vars_from_config(cls, func: Callable) -> dict:
        print(func.__name__)
        tool_path = inspect.getfile(func)
        print(tool_path)
        tool_parent = "/".join(tool_path.split("/")[:-1])
        tool_config_path = pathlib.Path(tool_parent) / "config.toml"
        with tool_config_path.open("r") as f:
            tool_config = toml.load(f)
            tool_vars = tool_config.get("tool_var")
            if not tool_vars:
                return 
            tool_vars_dict = {}
            for key, value in tool_vars.items():
                tool_vars_dict[key] = value
            return tool_vars_dict
