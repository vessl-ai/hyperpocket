from fastapi import APIRouter
from starlette.responses import HTMLResponse
from hyperpocket.futures import FutureStore

bitwarden_auth_router = APIRouter(prefix="/bitwarden")


@bitwarden_auth_router.get("/token/callback")
async def bitwarden_token_callback(state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")
    return HTMLResponse(content="success")
