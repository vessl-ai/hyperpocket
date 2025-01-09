from fastapi import APIRouter, Request
from starlette.responses import HTMLResponse

from hyperpocket.futures import FutureStore

calendly_auth_router = APIRouter(prefix="/calendly")


@calendly_auth_router.get("/oauth2/callback")
async def calendly_oauth2_callback(request: Request, state: str, code: str):
    try:
        FutureStore.resolve_future(state, code)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")
