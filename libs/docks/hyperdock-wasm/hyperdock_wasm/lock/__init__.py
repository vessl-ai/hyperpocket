from hyperdock_wasm.lock.git import GitWasmLock
from hyperdock_wasm.lock.local import LocalWasmLock

WasmLock = GitWasmLock | LocalWasmLock

__all__ = ["WasmLock", "GitWasmLock", "LocalWasmLock"]