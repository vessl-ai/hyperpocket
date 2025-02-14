import os
import traceback
from typing import Any, Callable, Optional, Tuple, Type

import multiprocess
from langchain.tools import BaseTool

from hyperdock_langchain.dictionary import EnvDict


class LangchainToolRequest(object):
    tool_type: Type[BaseTool]
    tool_args: dict[str, Any]
    env_dict_extends: dict[str, str]
    auth: Optional[dict[str, Any]]
    tool_vars: dict[str, str]

    def __init__(
        self,
        tool_type: Type[BaseTool],
        tool_args: Optional[dict[str, Any]] = None,
        env_dict_extends: Optional[dict[str, str]] = None,
        auth: Optional[dict[str, Any]] = None,
        tool_vars: Optional[dict[str, str]] = None,
    ):
        self.tool_type = tool_type
        self.tool_args = {}
        if tool_args is not None:
            self.tool_args = tool_args
        self.env_dict_extends = {}
        if env_dict_extends is not None:
            self.env_dict_extends = env_dict_extends
        self.auth = auth
        self.tool_vars = {}
        if tool_vars is not None:
            self.tool_vars = tool_vars


ToolType = Type[BaseTool] | LangchainToolRequest


def modify_environment(
    environ: dict[str, str],
    kwargs: dict[str, Any],
    env_dict_extends: dict[str, Callable[[str, str], Tuple[str, str]]],
) -> dict[str, str]:
    default_rules = EnvDict.default().rules
    for key, value in kwargs.items():
        if key in env_dict_extends:
            if (replacer := env_dict_extends.get(key)) is not None:
                k, v = replacer(key, value)
                environ[k] = v
        elif key in default_rules:
            if (replacer := default_rules.get(key)) is not None:
                k, v = replacer(key, value)
                environ[k] = v
    return environ


def _run(
    tool_type: Type[BaseTool],
    envs: dict[str, str],
    tool_kwargs: dict[str, Any],
    pipe: multiprocess.Pipe,
    **kwargs,
) -> None:
    # must be called in a child process
    for key, value in envs.items():
        os.environ[key] = value
    tool = tool_type(**tool_kwargs)
    config = {}
    if "config" in kwargs:
        config = kwargs.pop("config")
    result = tool.invoke(input=kwargs, config=config)
    _, conn = pipe
    conn.send(result)

# @moon: will be refactored
def connect(
    tool_type: ToolType,
) -> Callable[[...], str]:
    tool_req = tool_type
    if isinstance(tool_type, type):
        tool_req = LangchainToolRequest(tool_type)

    def wrapper(**kwargs) -> str:
        try:
            # replacement only happens when user uses pocket native auth
            if tool_req.auth is not None:
                child_env = modify_environment(
                    os.environ.copy(), kwargs, tool_req.env_dict_extends
                )
            else:
                child_env = os.environ.copy()
            pipe = multiprocess.Pipe()
            process = multiprocess.Process(
                target=_run,
                args=(tool_req.tool_type, child_env, tool_req.tool_args, pipe),
                kwargs=kwargs,
            )
            process.start()
            conn, _ = pipe
            while True:
                if conn.poll():
                    result = conn.recv()
                    break
            process.terminate()
            process.join()
            return result
        except Exception as e:
            return "\n".join(traceback.format_exception(e))

    wrapper.__name__ = tool_req.tool_type.__name__
    default_doc = tool_req.tool_type.__pydantic_fields__["description"].get_default()
    wrapper.__doc__ = (
        default_doc if default_doc is not None else tool_req.tool_type.__doc__
    )
    wrapper.__model__ = tool_req.tool_type.__pydantic_fields__[
        "args_schema"
    ].get_default()
    wrapper.__auth__ = tool_req.auth
    wrapper.__vars__ = tool_req.tool_vars

    return wrapper
