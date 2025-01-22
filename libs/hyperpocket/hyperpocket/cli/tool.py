import os
import subprocess
import click
from pathlib import Path

from hyperpocket.cli.codegen.tool import get_tool_main_template

@click.command()
@click.argument('tool_name', type=str)
def create_tool_template(tool_name):
    ## validate tool_name
    if not tool_name.islower() or not tool_name.replace('_', '').isalpha():
        raise ValueError("tool_name must be lowercase and contain only letters and underscores")
    
    tool_directory_name = tool_name.replace('_', '-')
    capitalized_tool_name = tool_name.capitalize()
    if '_' in tool_name:
        capitalized_tool_name = ''.join([word.capitalize() for word in tool_name.split('_')])
    
    ## create tool directory
    cwd = Path.cwd()
    tool_path = cwd / tool_directory_name
    if not os.path.exists(tool_path):
        os.makedirs(tool_path)
    
    ## create tool module directory
    tool_module_path = tool_path / tool_name
    if not os.path.exists(tool_module_path):
        os.makedirs(tool_module_path)
    
    ## create __init__.py file
    if not os.path.exists(tool_module_path / '__init__.py'):
        with open(tool_module_path / '__init__.py', "w") as f:
            f.write(f'''
from {tool_name}.__main__ import main

__all__ = ["main"]
''')
    
    ## create __main__.py file
    if not os.path.exists(tool_module_path / '__main__.py'):
        output_from_parsed_template = get_tool_main_template().render(
            capitalized_tool_name=capitalized_tool_name,
            tool_name=tool_name
        )
        breakpoint()
        with open(tool_module_path / '__main__.py', "w") as f:
            f.write(output_from_parsed_template)
    
    ## config.toml
    if not os.path.exists(tool_path / 'config.toml'):
        with open(tool_path / 'config.toml', "w") as f:
            f.write(f'''
name = "{tool_name}"
description = ""
language = ""

[auth]
auth_provider = ""
auth_handler = ""
scopes = []
''')
            
    ## .gitignore
    if not os.path.exists(tool_path / '.gitignore'):
        with open(tool_path / '.gitignore', "w") as f:
            pass
    
    ## README.md
    if not os.path.exists(tool_path / 'README.md'):
        with open(tool_path / 'README.md', "w") as f:
            f.write(f'# {tool_name}\n\n')
    
    ## schema.json
    if not os.path.exists(tool_path / 'schema.json'):
        with open(tool_path / 'schema.json', "w") as f:
            pass

@click.command()
@click.argument('tool_path', type=str, required=False)
def build_tool(tool_path):
    cwd = Path.cwd()
    
    ## If tool_path is not provided, cwd must be a tool directory
    if tool_path is None:
        if not os.path.exists(cwd / 'config.toml') :
            raise ValueError("Current working directory must be a tool directory")
    
    ## If tool_path is provided, change cwd to the tool directory
    else:
        if os.path.exists(cwd / tool_path):
            cwd = cwd / tool_path
        elif os.path.exists(tool_path):
            cwd = Path(tool_path)
        else:
            raise ValueError(f"Tool path '{tool_path}' does not exist")
        
    ## Build the tool 
    if os.path.exists(cwd / 'poetry.lock'):
        subprocess.run(["poetry", "build"], cwd=cwd, check=True) 
    elif os.path.exists(cwd / 'uv.lock'):
        subprocess.run(["uv", "build"], cwd=cwd, check=True) 
    else:
        raise ValueError("Tool must be a poetry or uv project")
