import os
import toml
import pathlib

def test_injecting_tool_var():
    config_path = pathlib.Path(os.getcwd()) / "config.toml"
    with config_path.open("r") as f:
        config = toml.load(f)
        if "tool_var" in config:
            tool_var = config["tool_var"]
    print(tool_var["config1"])
    print(tool_var["config2"])
    print(tool_var["config3"])
    return "Hello, World!"