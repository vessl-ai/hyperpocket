from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse

from hyperpocket.futures import FutureStore

gumloop_auth_router = APIRouter(prefix="/gumloop")


@gumloop_auth_router.get("/token/callback")
async def gumloop_oauth2_callback(request: Request, state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")
