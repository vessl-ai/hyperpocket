from hyperdock_wasm.tool_reference.git import WasmGitToolReference
from hyperdock_wasm.tool_reference.local import WasmLocalToolReference

WasmToolReference = WasmGitToolReference | WasmLocalToolReference

__all__ = ["WasmToolReference", "WasmGitToolReference", "WasmLocalToolReference"]