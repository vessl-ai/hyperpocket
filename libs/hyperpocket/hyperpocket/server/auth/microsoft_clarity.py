from fastapi import APIRouter
from starlette.responses import HTMLResponse
from hyperpocket.futures import FutureStore

microsoft_clarity_auth_router = APIRouter(prefix="/microsoft_clarity")


@microsoft_clarity_auth_router.get("/token/callback")
async def microsoft_clarity_token_callback(state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")
    return HTMLResponse(content="success")
