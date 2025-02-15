from fastapi import APIRouter
from starlette.responses import HTMLResponse
from hyperpocket.futures import FutureStore

alchemy_auth_router = APIRouter(prefix="/alchemy")


@alchemy_auth_router.get("/token/callback")
async def alchemy_token_callback(state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")
    return HTMLResponse(content="success")
