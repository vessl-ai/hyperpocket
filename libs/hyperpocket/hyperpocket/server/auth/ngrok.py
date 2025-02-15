from fastapi import APIRouter
from starlette.responses import HTMLResponse
from hyperpocket.futures import FutureStore

ngrok_auth_router = APIRouter(prefix="/ngrok")


@ngrok_auth_router.get("/token/callback")
async def ngrok_token_callback(state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")
    return HTMLResponse(content="success")
