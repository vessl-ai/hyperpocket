import os
import json
import sys
import shutil
import subprocess
from pathlib import Path
import importlib

import click

from hyperpocket.cli.codegen.tool import get_tool_main_template
from hyperpocket.util.flatten_json_schema import flatten_json_schema


@click.command()
@click.argument("tool_name", type=str)
def create_tool_template(tool_name, language="python"):
    """Create a tool template with the specified tool name."""

    # Validate tool_name
    if not tool_name.islower() or not tool_name.replace("_", "").isalpha():
        raise ValueError(
            "tool_name must be lowercase and contain only letters and underscores"
        )

    capitalized_tool_name = "".join(
        [word.capitalize() for word in tool_name.split("_")]
    )

    # Create tool directory
    print(f"Generating tool package directory for {tool_name}")
    cwd = Path.cwd()
    tool_path = cwd / tool_name
    tool_path.mkdir(parents=True, exist_ok=True)

    # Create uv or poetry init
    print(f"Generating pyproject.toml file for {tool_name}")
    if shutil.which("uv"):
        subprocess.run(["uv", "init"], cwd=tool_path, check=True)
        os.remove(tool_path / "hello.py")
    elif shutil.which("poetry"):
        subprocess.run(
            ["poetry", "init", "--no-interaction"], cwd=tool_path, check=True
        )
    else:
        raise ValueError("uv or poetry must be installed to generate tool project")

    # Create __init__.py file
    init_file = tool_path / "__init__.py"
    if not init_file.exists():
        init_file.write_text(f"""from .__main__ import main

__all__ = ["main"]
""")

    # Create __main__.py file
    print(f"Generating tool main file for {tool_name}")
    main_file = tool_path / "__main__.py"
    if not main_file.exists():
        main_content = get_tool_main_template().render(
            capitalized_tool_name=capitalized_tool_name, tool_name=tool_name
        )
        main_file.write_text(main_content)

    # Create pocket.json
    print(f"Generating pocket.json file for {tool_name}")
    pocket_dict = {
        "tool": {
            "name": tool_name,
            "description": "",
            "inputSchema": {
                "properties": {},
                "required": [],
                "title": f"{capitalized_tool_name}Request",
                "type": "object"
            }
        },
        "language": language,
        "auth": {
            "auth_provider": "",
            "auth_handler": "",
            "scopes": [],
        },
        "variables": {},
        "entrypoint": {
            "build": "pip install .",
            "run": "python __main__.py"
        }
    }
    pocket_json = json.dumps(pocket_dict, indent=2)
    pocket_file = tool_path / "pocket.json"
    pocket_file.write_text(pocket_json)
    
    # Create .gitignore
    print(f"Generating .gitignore file for {tool_name}")
    gitignore_file = tool_path / ".gitignore"
    gitignore_file.touch()

    # Create README.md
    print(f"Generating README.md file for {tool_name}")
    readme_file = tool_path / "README.md"
    if not readme_file.exists():
        readme_file.write_text(f"# {tool_name}\n\n")

@click.command()
@click.argument("tool_path", type=str, required=False)
def sync_tool_schema(tool_path):
    """Sync the schema of the tool at the main.py file from specified path or current directory."""

    cwd = Path.cwd()
    
    working_dir = cwd / tool_path
    if os.path.isabs(tool_path):
        working_dir = Path(tool_path)
        
    pocket_file = working_dir / "pocket.json"
    if not pocket_file.exists():
        raise ValueError("pocket.json file does not exist")

    with open(pocket_file, "r", encoding="utf-8") as f:
        pocket_dict = json.load(f)
    
    model_name = pocket_dict["tool"]["inputSchema"]["title"]
    
    model_object = import_class_from_file(working_dir / "__main__.py", model_name)

    schema_json = model_object.model_json_schema()
    flatten_schema_json = flatten_json_schema(schema_json)
    
    pocket_dict["tool"]["inputSchema"]["properties"] = flatten_schema_json["properties"]
    pocket_dict["tool"]["inputSchema"]["required"] = flatten_schema_json["required"]
    
    pocket_json = json.dumps(pocket_dict, indent=2)
    pocket_file.write_text(pocket_json)
    
def import_class_from_file(file_path: Path, class_name: str):
    """Import a class from a Python file using its path and class name."""
    spec = importlib.util.spec_from_file_location(class_name, file_path)
    
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        sys.modules[class_name] = module
        spec.loader.exec_module(module)

        if hasattr(module, class_name):
            return getattr(module, class_name)
        else:
            raise AttributeError(f"Class '{class_name}' not found in {file_path}")
    else:
        raise ImportError(f"Could not load module from {file_path}")
