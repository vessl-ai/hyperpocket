import os
import shutil
import subprocess
from pathlib import Path

import click

from hyperpocket.cli.codegen.tool import get_tool_main_template


@click.command()
@click.argument("tool_name", type=str)
def create_tool_template(tool_name, language="python"):
    """Create a tool template with the specified tool name."""

    # Validate tool_name
    if not tool_name.islower() or not tool_name.replace("_", "").isalpha():
        raise ValueError(
            "tool_name must be lowercase and contain only letters and underscores"
        )

    tool_directory_name = tool_name.replace("_", "-")
    capitalized_tool_name = "".join(
        [word.capitalize() for word in tool_name.split("_")]
    )

    # Create tool directory
    print(f"Generating tool package directory for {tool_name}")
    cwd = Path.cwd()
    tool_path = cwd / tool_directory_name
    tool_path.mkdir(parents=True, exist_ok=True)

    # Create tool module directory
    print(f"Generating tool module directory for {tool_name}")
    tool_module_path = tool_path / tool_name
    tool_module_path.mkdir(parents=True, exist_ok=True)

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
    init_file = tool_module_path / "__init__.py"
    if not init_file.exists():
        init_file.write_text(f"""from .__main__ import main

__all__ = ["main"]
""")

    # Create __main__.py file
    print(f"Generating tool main file for {tool_name}")
    main_file = tool_module_path / "__main__.py"
    if not main_file.exists():
        main_content = get_tool_main_template().render(
            capitalized_tool_name=capitalized_tool_name, tool_name=tool_name
        )
        main_file.write_text(main_content)

    # Create config.toml
    print(f"Generating config.toml file for {tool_name}")
    config_file = tool_path / "config.toml"
    if not config_file.exists():
        config_file.write_text(f'''name = "{tool_name}"
description = ""
language = "{language}"

[auth]
auth_provider = ""
auth_handler = ""
scopes = []
''')

    # Create .gitignore
    print(f"Generating .gitignore file for {tool_name}")
    gitignore_file = tool_path / ".gitignore"
    gitignore_file.touch()

    # Create README.md
    print(f"Generating README.md file for {tool_name}")
    readme_file = tool_path / "README.md"
    if not readme_file.exists():
        readme_file.write_text(f"# {tool_name}\n\n")

    # Create schema.json
    print(f"Generating schema.json file for {tool_name}")
    schema_file = tool_path / "schema.json"
    schema_file.touch()


@click.command()
@click.argument("tool_path", type=str, required=False)
def build_tool(tool_path):
    """Build the tool at the specified path or current directory."""

    cwd = Path.cwd()

    # Determine the tool directory
    if tool_path is None:
        if not (cwd / "config.toml").exists():
            raise ValueError("Current working directory must be a tool directory")
    else:
        potential_path = Path(tool_path)
        if (cwd / potential_path).exists():
            cwd = cwd / potential_path
        elif potential_path.exists():
            cwd = potential_path
        else:
            raise ValueError(f"Tool path '{tool_path}' does not exist")

    # Build the tool
    print(f"Building tool in {cwd}")
    if shutil.which("uv"):
        subprocess.run(["uv", "build"], cwd=cwd, check=True)
        os.remove(cwd / "dist/.gitignore")
    elif shutil.which("poetry"):
        subprocess.run(["poetry", "build"], cwd=cwd, check=True)
    else:
        raise ValueError("Tool must be a poetry or uv project")
