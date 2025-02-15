from fastapi import APIRouter
from starlette.responses import HTMLResponse
from hyperpocket.futures import FutureStore

mailchimp_auth_router = APIRouter(prefix="/mailchimp")


@mailchimp_auth_router.get("/oauth2/callback")
async def mailchimp_oauth2_callback(state: str, code: str):
    try:
        FutureStore.resolve_future(state, code)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")


@mailchimp_auth_router.get("/token/callback")
async def mailchimp_token_callback(state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")
