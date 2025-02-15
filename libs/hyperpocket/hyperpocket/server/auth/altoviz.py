from fastapi import APIRouter
from starlette.responses import HTMLResponse
from hyperpocket.futures import FutureStore

altoviz_auth_router = APIRouter(prefix="/altoviz")


@altoviz_auth_router.get("/token/callback")
async def altoviz_token_callback(state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")
    return HTMLResponse(content="success")
