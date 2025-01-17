import copy
import inspect
from typing import Callable, Awaitable, Optional

from pydantic import BaseModel

from hyperpocket.tool.tool import Tool, ToolAuth
from hyperpocket.util.flatten_json_schema import flatten_json_schema
from hyperpocket.util.function_to_model import function_to_model


class FunctionTool(Tool):
    """
    FunctionTool is Tool executing local python method.
    """
    func: Callable
    afunc: Optional[Callable[..., Awaitable[str]]]

    def invoke(self, **kwargs) -> str:
        binding_args = self._get_binding_args(kwargs)
        return str(self.func(**binding_args))

    async def ainvoke(self, **kwargs) -> str:
        binding_args = self._get_binding_args(kwargs)
        if self.afunc is None:
            return str(self.func(**binding_args))
        return str(await self.afunc(**binding_args))

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
                binding_args |= _kwargs.get("envs", {})

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
        func: Callable,
        afunc: Callable[..., Awaitable[str]] = None,
        auth: Optional[ToolAuth] = None
    ) -> "FunctionTool":
        model = function_to_model(func)
        argument_json_schema = flatten_json_schema(model.model_json_schema())

        return cls(
            func=func,
            afunc=afunc,
            name=func.__name__,
            description=model.__doc__,
            argument_json_schema=argument_json_schema,
            auth=auth
        )
    
    @classmethod
    def from_dock(
        cls,
        dock: list[Callable[..., str]],
    ) -> "FunctionTool":
        for func in dock:
            model = function_to_model(func)
            argument_json_schema = flatten_json_schema(model.model_json_schema())
            if not callable(func):
                raise ValueError(f"Dock element should be a list of functions, but found {func}")
            is_coro = inspect.iscoroutinefunction(func)
            auth = None,
            if func.__dict__.get("__auth__"):
                auth = ToolAuth(**func.__dict__["__auth__"])
            if is_coro:
                return cls(
                    afunc=func,
                    name=func.__name__,
                    description=func.__doc__,
                    argument_json_schema=argument_json_schema,
                    auth=auth,
                )