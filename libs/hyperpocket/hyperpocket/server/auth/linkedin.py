from fastapi import APIRouter
from starlette.responses import HTMLResponse
from hyperpocket.futures import FutureStore

linkedin_auth_router = APIRouter(prefix="/linkedin")


@linkedin_auth_router.get("/oauth2/callback")
async def linkedin_oauth2_callback(state: str, code: str):
    try:
        FutureStore.resolve_future(state, code)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")


@linkedin_auth_router.get("/token/callback")
async def linkedin_token_callback(state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")
