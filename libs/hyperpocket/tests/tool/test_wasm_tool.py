import pathlib
from tempfile import TemporaryDirectory
from unittest import TestCase

from hyperpocket.repository import Lockfile
from hyperpocket.tool import from_local
from hyperpocket.tool.wasm import WasmTool
from hyperpocket.tool.wasm.invoker import WasmInvoker


class TestWasmTool(TestCase):
    class MockInvoker(WasmInvoker):
        def invoke(self, tool_path, runtime, body, envs, **kwargs):
            return str(int(envs["a"]) + int(envs["b"]))

        async def ainvoke(self, tool_path, runtime, body, envs, **kwargs):
            return str(int(envs["a"]) + int(envs["b"]))

    def test_wasm_tool_vars_inject(self):
        with TemporaryDirectory() as tool_dir:
            with open(f"{tool_dir}/schema.json", "w") as f:
                f.write("{}")
            with open(f"{tool_dir}/config.toml", "w") as f:
                f.write("""
name = "mock"
description = "mock"
language = "python"

[tool_vars]
a = "1"
b = "2"
""")
            with open(f"{tool_dir}/README.md", "w") as f:
                f.write("mock")
            lockfile = Lockfile(pathlib.Path(tool_dir) / ".lock")
            req = from_local(tool_dir)
            lockfile.add_lock(req.lock)
            lockfile.sync(False)
            tool = WasmTool.from_tool_request(req, lockfile=lockfile)
            tool._invoker = self.MockInvoker()
            tool.override_tool_variables({"a": "1", "b": "1"})
            self.assertEqual(tool.invoke(body={}, envs={}), "2")

    def test_wasm_tool_vars_inject_with_from_local(self):
        with TemporaryDirectory() as tool_dir:
            with open(f"{tool_dir}/schema.json", "w") as f:
                f.write("{}")
            with open(f"{tool_dir}/config.toml", "w") as f:
                f.write("""
name = "mock"
description = "mock"
language = "python"

[tool_vars]
a = "1"
b = "2"
""")
            with open(f"{tool_dir}/README.md", "w") as f:
                f.write("mock")
            lockfile = Lockfile(pathlib.Path(tool_dir) / ".lock")
            req = from_local(tool_dir, tool_vars={"a": "1", "b": "1"})
            lockfile.add_lock(req.lock)
            lockfile.sync(False)
            tool = WasmTool.from_tool_request(req, lockfile=lockfile)
            tool._invoker = self.MockInvoker()
            self.assertEqual(tool.invoke(body={}, envs={}), "2")
