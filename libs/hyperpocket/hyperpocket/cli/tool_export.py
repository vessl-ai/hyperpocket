import os
import re
import ast
import json
import toml
import importlib
import inspect
import shutil
from typing import Callable
from pathlib import Path
import click

from hyperpocket.cli.tool_create import create_tool_template


@click.command()
@click.argument("target", type=str, required=False)
def export_tool(target, language="python"):
    """Convert the specified tool to a local tool."""

    target_path = Path.cwd() / target if target else Path.cwd()

    if target_path.is_file():
        process_tool_file(target_path, language)
    elif target_path.is_dir():
        process_tool_directory(target_path, language)
    else:
        raise ValueError("Invalid target path")


def process_tool_file(target_path: Path, language: str):
    """Process a single Python file containing function_tool decorated functions."""
    decorated_functions = find_function_tool_decorated_functions(target_path)

    if not decorated_functions:
        raise ValueError("No function_tool decorated functions found in target file")
    if len(decorated_functions) > 1:
        raise ValueError(
            "Multiple function_tool decorated functions found in target file"
        )

    func = load_functions_as_callable(decorated_functions, target_path)
    tool_name = func.func.__name__.replace("-", "_")
    cleaned_code = clean_tool_source_code(target_path.read_text())
    tool_main_code = transform_function_to_pydantic(cleaned_code, func)

    generate_tool_template(tool_name)
    generate_tool_files(target_path, tool_name, tool_main_code, func, language)


def process_tool_directory(target_path: Path, language: str):
    """Process a directory containing function_tool decorated functions."""
    decorated_function_file = None

    for file in target_path.glob("*.py"):
        decorated_functions = find_function_tool_decorated_functions(file)
        if len(decorated_functions) == 1:
            decorated_function_file = file
            break
        elif len(decorated_functions) > 1:
            raise ValueError(
                "Multiple function_tool decorated functions found in target file"
            )

    if not decorated_function_file:
        raise ValueError(
            "No function_tool decorated functions found in target directory"
        )

    func = load_functions_as_callable(decorated_functions, decorated_function_file)
    tool_name = func.func.__name__.replace("-", "_")
    cleaned_code = clean_tool_source_code(decorated_function_file.read_text())
    tool_main_code = transform_function_to_pydantic(cleaned_code, func)

    if tool_name != decorated_function_file.stem:
        raise ValueError("Tool name must match the file name")

    generate_tool_template(tool_name)
    copy_tool_directory(target_path, tool_name)
    generate_tool_files(target_path, tool_name, tool_main_code, func, language)


def find_function_tool_decorated_functions(file_path: Path):
    """Find all functions decorated with @function_tool in a given Python file."""
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    tree = ast.parse(source_code)
    decorated_functions = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        and any(
            isinstance(decorator, ast.Call) and decorator.func.id == "function_tool"
            for decorator in node.decorator_list
        )
    ]

    return decorated_functions


def load_functions_as_callable(decorated_functions, file_path: Path):
    """Load function_tool decorated function as a callable object."""
    module_name = file_path.stem
    spec = importlib.util.spec_from_file_location(module_name, str(file_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, decorated_functions[0])


def clean_tool_source_code(source_code: str) -> str:
    """Remove hyperpocket import, function_tool decorator, and main execution block."""
    source_code = re.sub(
        r"^from hyperpocket\.tool .*?\n", "", source_code, flags=re.MULTILINE
    )
    source_code = re.sub(
        r"@function_tool\([\s\S]*?\)\n", "", source_code, flags=re.MULTILINE
    )
    source_code = re.sub(
        r"\nif __name__ == [\"']__main__[\"']:[\s\S]*",
        "",
        source_code,
        flags=re.MULTILINE,
    )
    return source_code.strip()


def transform_function_to_pydantic(tool_source_code: str, func: Callable):
    """Transform function into a Pydantic-based CLI tool."""
    function_code = extract_function_code(func)

    tree = ast.parse(function_code)
    function_name = func.func.__name__

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            params = {
                arg.arg: arg.annotation.id
                for arg in node.args.args
                if isinstance(arg.annotation, ast.Name)
            }
            properties = func.argument_json_schema["properties"]

            model_name = function_name.title().replace("_", "") + "Request"
            model_fields = [
                f'    {name}: {type_} = Field(..., description="{properties[name]["description"]}")'
                for name, type_ in params.items()
            ]
            model_code = (
                f"class {model_name}(BaseModel):\n" + "\n".join(model_fields) + "\n"
            )

            main_code = f"""def main():
    req = json.load(sys.stdin.buffer)
    req_typed = {model_name}.model_validate(req)
    response = {function_name}(**req_typed.model_dump())

    print(json.dumps(response))


if __name__ == "__main__":
    main()
"""
            import_code = """import json
import os
import sys

from pydantic import BaseModel, Field
"""
            return (
                import_code
                + "\n"
                + tool_source_code
                + "\n\n"
                + model_code
                + "\n"
                + main_code
            )

    return None


def extract_function_code(func: Callable) -> str:
    """Extract function definition as a string."""
    tool_source_code = inspect.getsource(func.func.__code__)
    match = re.search(r"def\s+\w+\(.*\):[\s\S]*", tool_source_code)
    return match.group(0) if match else ""


def generate_tool_template(tool_name: str):
    """Generate tool template using Click context forwarding."""
    ctx = click.Context(create_tool_template)
    ctx.forward(create_tool_template, tool_name=tool_name)


def copy_tool_directory(src_path: Path, tool_name: str):
    """Copy the tool directory to the new tool directory."""
    tool_directory_name = tool_name.replace("_", "-")
    dst_path = src_path.parent / tool_directory_name / tool_name

    if dst_path.exists():
        shutil.rmtree(dst_path)

    shutil.copytree(src_path, dst_path)
    os.remove(dst_path / f"{tool_name}.py")

    init_file = src_path.parent / tool_directory_name / tool_name / "__init__.py"
    init_file.write_text(f"from .__main__ import main\n\n__all__ = ['main']")


def generate_tool_files(
    target_path: Path,
    tool_name: str,
    tool_main_code: str,
    func: Callable,
    language: str,
):
    """Generate config.toml, __main__.py, and schema.json for the tool."""
    tool_directory_name = tool_name.replace("_", "-")

    config_file = target_path.parent / tool_directory_name / "config.toml"
    config_data = {
        "name": func.name,
        "description": func.description,
        "language": language,
        "auth": json.loads(func.auth.model_dump_json()),
        "tool_vars": func.default_tool_vars,
    }

    with open(config_file, "w", encoding="utf-8") as f:
        f.write(toml.dumps(config_data))

    main_file = target_path.parent / tool_directory_name / tool_name / "__main__.py"
    with open(main_file, "w", encoding="utf-8") as f:
        f.write(tool_main_code)

    schema_file = target_path.parent / tool_directory_name / "schema.json"
    with open(schema_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(func.argument_json_schema, indent=4))
