from fastapi import APIRouter
from starlette.responses import HTMLResponse

from hyperpocket.futures import FutureStore

reddit_auth_router = APIRouter(prefix="/reddit")


@reddit_auth_router.get("/oauth2/callback")
async def reddit_oauth2_callback(state: str, code: str):
    try:
        FutureStore.resolve_future(state, code)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")
