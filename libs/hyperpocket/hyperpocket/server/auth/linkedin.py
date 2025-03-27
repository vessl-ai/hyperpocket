from fastapi import APIRouter
from hyperpocket.config.auth import DefaultAuthConfig
from starlette.responses import HTMLResponse
from hyperpocket.futures import FutureStore
from cryptography.fernet import Fernet

linkedin_auth_router = APIRouter(prefix="/linkedin")


@linkedin_auth_router.get("/oauth2/callback")
async def linkedin_oauth2_callback(state: str, code: str):
    try:
        FutureStore.resolve_future(state, code)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")


@linkedin_auth_router.get("/basicauth/callback")
async def linkedin_basicauth_callback(state: str, token: str):
    try:
        key = DefaultAuthConfig.secret_key.encode()
        decrypted = Fernet(key).decrypt(token.encode()).decode()
        FutureStore.resolve_future(state, decrypted)
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")
