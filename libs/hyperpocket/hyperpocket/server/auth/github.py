from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse

from hyperpocket.futures import FutureStore

github_auth_router = APIRouter(prefix="/github")


@github_auth_router.get("/oauth2/callback")
async def github_oauth2_callback(request: Request, state: str, code: str):
    try:
        FutureStore.resolve_future(state, code)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")


@github_auth_router.get("/token/callback")
async def github_token_callback(request: Request, state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")
