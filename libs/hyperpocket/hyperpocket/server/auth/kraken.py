from http import HTTPStatus

from fastapi import APIRouter, Form
from starlette.responses import HTMLResponse, RedirectResponse
from hyperpocket.futures import FutureStore
from hyperpocket.server.auth.token import add_query_params

kraken_auth_router = APIRouter(prefix="/kraken")

@kraken_auth_router.get("/keypair", response_class=HTMLResponse)
async def keypair_form(redirect_uri: str, state: str = ""):
    html = f"""    
    <html>
        <body>
            <h2>Enter Token</h2>
            <form action="submit" method="post">
                <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                <input type="hidden" name="state" value="{state}">
                
                <label for="kraken_api_key">Kraken API Key:</label>
                <input type="text" id="kraken_api_key" name="kraken_api_key" required>
                
                <label for="kraken_api_secret">Kraken API Secret:</label>
                <input type="text" id="kraken_api_secret" name="kraken_api_secret" required>
                
                <button type="submit">submit</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html)

@kraken_auth_router.post("/submit", response_class=RedirectResponse)
async def submit_keypair(
    kraken_api_key: str = Form(...),
    kraken_api_secret: str = Form(...),
    redirect_uri: str = Form(...),
    state: str = Form(...),
):
    new_callback_url = add_query_params(
        redirect_uri, {
            "kraken_api_key": kraken_api_key,
            "kraken_api_secret": kraken_api_secret,
            "state": state,
        }
    )
    return RedirectResponse(url=new_callback_url, status_code=HTTPStatus.SEE_OTHER)

@kraken_auth_router.get("/keypair/callback")
async def kraken_keypair_callback(state: str, kraken_api_key: str, kraken_api_secret: str):
    try:
        FutureStore.resolve_future(state, {
            "kraken_api_key": kraken_api_key,
            "kraken_api_secret": kraken_api_secret,
        })
    except ValueError:
        return HTMLResponse(content="failed")
    return HTMLResponse(content="success")
