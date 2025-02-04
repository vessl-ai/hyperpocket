import json
import os
import pathlib
import re
import shutil
import subprocess
import tomlkit


def build_python_tool(
        base_path: pathlib.Path,
        tool_name: str,
        tool_description: str,
        language: str,
        code: str,
        auth_provider: str = None,
        auth_handler: str = None,
        scopes: list = None,
        dependencies: list = None):
    if scopes is None:
        scopes = []
    if dependencies is None:
        dependencies = []

    tool_path = base_path / tool_name
    if tool_path.exists():
        print("delete ", tool_path)
        shutil.rmtree(tool_path)

    _init_uv(tool_path, tool_name, dependencies)
    _create_tool_metadata(auth_provider, auth_handler, language, scopes, tool_description, tool_name, tool_path)
    _create_tool_code(code, tool_name, tool_path)
    _build_uv(tool_path)


def _init_uv(tool_path: pathlib.Path, tool_name: str, dependencies):
    # init uv
    output = subprocess.run(
        ["uv", "init", "--no-workspace", tool_name], cwd=tool_path.parent,
        capture_output=True,
        text=True)

    if output.returncode != 0:
        print("error in uv init ", output)
        raise RuntimeError(f"error in uv init. {output}")
    print("uv init output : ", output)

    if (tool_path / "hello.py").exists():
        os.remove(tool_path / "hello.py")

    for dep in dependencies:
        output = subprocess.run(["uv", "add", dep], cwd=tool_path,
                                capture_output=True)
        if output.returncode != 0:
            raise RuntimeError(f"can't install package {dep}. {output.stderr.decode('utf-8')}")


def _create_tool_metadata(auth_provider, auth_handler, language, scopes, tool_description, tool_name, tool_path):
    # write config.toml
    with open(tool_path / "config.toml", "w") as f:
        data = {
            "name": tool_name,
            "description": tool_description,
            "language": language,
        }

        auth = {}
        if auth_provider:
            auth["auth_provider"] = auth_provider
        if auth_handler:
            auth["auth_handler"] = auth_handler
        if scopes:
            if isinstance(scopes, str):
                scopes = re.split(r'[,\s]+', scopes)
            auth["scopes"] = scopes

        if auth:
            data["auth"] = auth
        tomlkit.dump(data, f)

    # write schema.json
    with open(tool_path / "schema.json", "w") as f:
        json.dump({
            "title": f"{tool_name}ReqeustSchema",
            "type": "object",
            "properties": {
                "encoded_image": {
                    "title": "encoded_image",
                    "type": "string",
                    "description": "base64 encoded image string."
                }
            },
            "required": ["encoded_image"]
        }, f)

    with open(tool_path / "README.md", "a") as f:
        f.write(tool_name)


def _create_tool_code(code, tool_name, tool_path):
    # write code
    code_path = tool_path / tool_name
    if not os.path.exists(code_path):
        os.makedirs(code_path)
    with open(code_path / "__main__.py", "w") as f:
        full_code = f"""
{code}

def main(encoded_image):
    print(flip_your_picture(encoded_image))

if __name__ == "__main__":
  import json
  
  req = json.load(sys.stdin.buffer)
  main(req["encoded_image"])
"""
        f.write(full_code)
    with open(code_path / "__init__.py", "w") as f:
        f.write(
            f"""from {tool_name}.__main__ import main

__all__ = ["main"]
    """)


def _build_uv(tool_path: pathlib.Path):
    output = subprocess.run(
        ["uv", "build", "./"], cwd=tool_path,
        capture_output=True,
        text=True)
    if output.returncode != 0:
        print("error in uv build ", output)
        raise RuntimeError(f"error in uv build. {output}")

    dist_gitignore_path = tool_path / "dist/.gitignore"
    if dist_gitignore_path.exists():
        os.remove(dist_gitignore_path)

    print("uv build output : ", output)
