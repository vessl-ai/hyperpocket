from http import HTTPStatus
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from fastapi import APIRouter, Form
from starlette.responses import HTMLResponse, RedirectResponse

token_router = APIRouter()


@token_router.get("/token", response_class=HTMLResponse)
async def token_form(redirect_uri: str, state: str = ""):
    html = f"""    
    <html>
        <body>
            <h2>Enter Token</h2>
                     <form action="submit" method="post">
                <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                <input type="hidden" name="state" value="{state}">
                
                <label for="user_token">Token:</label>
                <input type="text" id="user_token" name="user_token" required>
                
                <button type="submit">submit</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html)


@token_router.post("/submit", response_class=RedirectResponse)
async def submit_token(
    user_token: str = Form(...), redirect_uri: str = Form(...), state: str = Form(...)
):
    new_callback_url = add_query_params(
        redirect_uri, {"token": user_token, "state": state}
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
