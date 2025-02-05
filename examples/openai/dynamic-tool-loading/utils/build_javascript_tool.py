import json
import os
import pathlib
import re
import shutil
import subprocess

import tomlkit


def build_javascript_tool(
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

    _init_npm(tool_path, dependencies)
    _create_tool_metadata(auth_provider, auth_handler, language, scopes, tool_description, tool_name, tool_path)
    _create_tool_code(code, tool_path)
    _build_npm(tool_path)


def _init_npm(tool_path: pathlib.Path, dependencies):
    if not tool_path.exists():
        os.makedirs(tool_path)

    output = subprocess.run(['npm', 'init', "-y"], cwd=tool_path,
                            capture_output=True,
                            text=True)

    if output.returncode != 0:
        print("error in npm init", output)
        raise RuntimeError(f"error in npm init {output}")

    subprocess.run(["npm", "set-script", "build", "ncc build index.js -o dist"], cwd=tool_path)
    subprocess.run(["npm", "install", "--save-dev", "@vercel/ncc"], cwd=tool_path)

    for dep in dependencies:
        output = subprocess.run(["npm", "install", dep], cwd=tool_path, capture_output=True)
        if output.returncode != 0:
            raise RuntimeError(f"can't install package {dep}. {output.stderr.decode('utf-8')}")


def _create_tool_metadata(auth_provider, auth_handler, language, scopes, tool_description, tool_name, tool_path):
    # write config.toml
    if language == "javascript":
        language = "node"  # to compatability with hyperpocket

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
        json.dump({"title": f"{tool_name}ReqeustSchema"}, f)


def _create_tool_code(code, tool_path):
    with open(tool_path / "index.js", "w") as f:
        f.write(
            f"""{code}

async function main() {{
    const result = guess_bulls_and_cows()
    console.log(result)
}}

main().catch(console.error).finally(() => process.exit());
"""
        )


def _build_npm(tool_path):
    output = subprocess.run(["npm", "run", "build"], cwd=tool_path,
                            capture_output=True,
                            text=True)

    if output.returncode != 0:
        print("error in npm build ", output)
        raise RuntimeError(f"error in npm build. {output}")
    print("npm build output : ", output)
