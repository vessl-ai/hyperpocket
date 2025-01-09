from fastapi import APIRouter

from hyperpocket.server.tool.wasm import wasm_tool_router

tool_router = APIRouter(
    prefix="/tools",
)
tool_router.include_router(wasm_tool_router)

__all__ = ["tool_router"]
