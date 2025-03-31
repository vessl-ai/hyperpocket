from cryptography.fernet import Fernet
from fastapi import APIRouter
from starlette.responses import HTMLResponse

from hyperpocket.config import config
from hyperpocket.futures import FutureStore

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
        key = config().auth.auth_encryption_secret_key.encode()
        decrypted = Fernet(key).decrypt(token.encode()).decode()
        FutureStore.resolve_future(state, decrypted)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")
