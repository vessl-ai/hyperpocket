from fastapi import APIRouter
from starlette.responses import HTMLResponse

from hyperpocket.futures import FutureStore

api_token_auth_router = APIRouter(prefix="/api-token")


@api_token_auth_router.get("/token/callback")
async def notion_token_callback(state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")
