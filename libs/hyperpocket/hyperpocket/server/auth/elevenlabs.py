from fastapi import APIRouter
from starlette.responses import HTMLResponse
from hyperpocket.futures import FutureStore

elevenlabs_auth_router = APIRouter(prefix="/elevenlabs")


@elevenlabs_auth_router.get("/token/callback")
async def elevenlabs_token_callback(state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")
    return HTMLResponse(content="success")
