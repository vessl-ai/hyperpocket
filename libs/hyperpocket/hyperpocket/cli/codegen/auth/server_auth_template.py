from jinja2 import Template


def get_server_auth_token_template() -> Template:
    return Template("""\
from fastapi import APIRouter
from starlette.responses import HTMLResponse
from hyperpocket.futures import FutureStore

{{ service_name }}_auth_router = APIRouter(
    prefix="/{{ service_name }}"
)


@{{ service_name }}_auth_router.get("/oauth2/callback")
async def {{ service_name }}_oauth2_callback(state: str, code: str):
    try:
        FutureStore.resolve_future(state, code)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")


@{{ service_name }}_auth_router.get("/token/callback")
async def {{ service_name }}_token_callback(state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")
""")


def get_server_auth_oauth2_template() -> Template:
    return Template("""\
from fastapi import APIRouter
from starlette.responses import HTMLResponse
from hyperpocket.futures import FutureStore

{{ service_name }}_auth_router = APIRouter(
    prefix="/{{ service_name }}"
)


@{{ service_name }}_auth_router.get("/oauth2/callback")
async def {{ service_name }}_oauth2_callback(state: str, code: str):
    try:
        FutureStore.resolve_future(state, code)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")


@{{ service_name }}_auth_router.get("/token/callback")
async def {{ service_name }}_token_callback(state: str, token: str):
    try:
        FutureStore.resolve_future(state, token)
    except ValueError:
        return HTMLResponse(content="failed")

    return HTMLResponse(content="success")
""")
