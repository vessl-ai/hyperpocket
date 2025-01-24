import httpx
from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse

from hyperpocket.config import config, pocket_logger


async def proxy(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=f"{config().internal_base_url}/{path}",
            headers=request.headers,
            content=await request.body(),
            params=request.query_params,
            timeout=300,
        )
        return HTMLResponse(
            content=resp.text, headers=resp.headers, status_code=resp.status_code
        )


def add_callback_proxy(app: FastAPI):
    app.add_api_route(
        f"/{config().callback_url_rewrite_prefix}/{{path:path}}",
        proxy,
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    )


https_proxy_app = None
if config().enable_local_callback_proxy:
    https_proxy_app = FastAPI()
    add_callback_proxy(https_proxy_app)


def _generate_ssl_certificates(ssl_keypath, ssl_certpath):
    import subprocess

    pocket_logger.info("generate default ssl file")

    subj = (
        "/C=US"
        "/ST=California"
        "/L=San Jose"
        "/O=local"
        "/OU=local"
        "/CN=localhost"
        "/emailAddress=local@example.com"
    )
    command = [
        "openssl",
        "req",
        "-x509",
        "-newkey",
        "rsa:4096",
        "-keyout",
        ssl_keypath,
        "-out",
        ssl_certpath,
        "-days",
        "1",
        "-nodes",
        "-subj",
        subj,
        "-sha256",
    ]

    try:
        # 명령 실행
        subprocess.run(
            command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        pocket_logger.info(
            "SSL Certificates generated: callback_server.key, callback_server.crt"
        )
    except subprocess.CalledProcessError as e:
        pocket_logger.warning(f"An error occurred while generating certificates: {e}")
        raise e
