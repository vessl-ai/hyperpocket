import base64
from http import HTTPStatus
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from cryptography.fernet import Fernet
from fastapi import APIRouter, Form
from starlette.responses import HTMLResponse, RedirectResponse

from hyperpocket.config import config
from hyperpocket.config.auth import DefaultAuthConfig
from hyperpocket.futures import FutureStore

default_router = APIRouter()


@default_router.get("/basicauth", response_class=HTMLResponse)
async def basicauth_form(redirect_uri: str, state: str = ""):
    html = f"""    
    <html>
        <body>
            <h2>Enter ID and Password</h2>
                     <form action="submit" method="post">
                <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                <input type="hidden" name="state" value="{state}">
                
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
                
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
                
                <button type="submit">submit</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html)


@default_router.post("/submit", response_class=RedirectResponse)
async def submit_basicauth(
    username: str = Form(...),
    password: str = Form(...),
    redirect_uri: str = Form(...),
    state: str = Form(...),
):
    token = f"{username}:{password}"
    base64_token = base64.b64encode(token.encode()).decode("utf-8")
    key = config().auth.auth_encryption_secret_key.encode()
    encrypted = Fernet(key).encrypt(base64_token.encode()).decode()
    new_callback_url = add_query_params(
        redirect_uri, {"token": encrypted, "state": state}
    )
    return RedirectResponse(url=new_callback_url, status_code=HTTPStatus.SEE_OTHER)


def add_query_params(url: str, params: dict):
    url_parts = urlparse(url)
    query_params = parse_qs(url_parts.query)
    query_params.update(params)
    new_query = urlencode(query_params, doseq=True)

    new_url = urlunparse(
        (
            url_parts.scheme,
            url_parts.netloc,
            url_parts.path,
            url_parts.params,
            new_query,
            url_parts.fragment,
        )
    )
    return new_url


basicauth_router = APIRouter(prefix="/basicauth")


@basicauth_router.get("/basicauth/callback")
async def basicauth_basicauth_callback(state: str, token: str):
    try:
        key = DefaultAuthConfig.auth_encryption_secret_key.encode()
        decrypted = Fernet(key).decrypt(token.encode()).decode()
        FutureStore.resolve_future(state, decrypted)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")
