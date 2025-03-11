import asyncio
import threading
from typing import Optional

from fastapi import FastAPI
from uvicorn import Config, Server

from hyperpocket.config import config, pocket_logger
from hyperpocket.server.auth import auth_router


class PocketServer(object):
    _instance: "PocketServer" = None

    fastapi_app: Optional[FastAPI]
    main_server: Optional[Server]
    internal_server_port: int
    proxy_server: Optional[Server]
    proxy_port: int

    thread: threading.Thread
    _initialized: bool
    _initialization_event: threading.Event
    _initialization_error: Optional[Exception]

    def __init__(self):
        self._initialized = False
        self._initialization_event = threading.Event()
        self._initialization_error = None

        self.internal_server_port = config().internal_server_port
        self.proxy_port = config().public_server_port
        self.fastapi_app = None
        self.main_server = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._instance.run()
        return cls._instance

    def teardown(self):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(self._teardown())
        loop.close()

    async def _teardown(self):
        if self.thread.is_alive():
            if self.main_server:
                self.main_server.should_exit = True
            if self.proxy_server:
                self.proxy_server.should_exit = True

            while self.thread.is_alive():
                await asyncio.sleep(0)

        self.thread.join()

    def run(self):
        self.thread = threading.Thread(
            target=self._run,
            daemon=True
        )
        self.thread.start()
        self._wait_initialized()

    def _run(self):
        try:
            # init process
            self.fastapi_app = self._create_fastapi_app()
            self.main_server = self._create_main_server(self.fastapi_app)
            self.proxy_server = self._create_https_proxy_server()
            self._report_initialized()

            loop = asyncio.new_event_loop()
            error = loop.run_until_complete(self._run_async())
            loop.close()

            if error:
                raise error

        except Exception as error:
            self._report_initialized(error)

    async def _run_async(self):
        try:
            await asyncio.gather(
                self.main_server.serve(),
                self.proxy_server.serve()
                if self.proxy_server is not None
                else asyncio.sleep(0),
                return_exceptions=True
            )
            return None
        except Exception as e:
            pocket_logger.warning(f"failed to start pocket server. error : {e}")
            return e

    def _report_initialized(self, error: Optional[Exception] = None):
        if error:
            pocket_logger.warning(f"Server initialization failed: {error}")
            self._initialization_error = error
        self._initialization_event.set()

    def _wait_initialized(self):
        if self._initialized:
            return

        self._initialization_event.wait()
        if self._initialization_error:
            raise self._initialization_error

        self._initialization_event.clear()
        self._initialized = True

    def _create_fastapi_app(self) -> FastAPI:
        app = FastAPI()
        app.add_api_route("/health", lambda: {"status": "ok"}, methods=["GET"])
        app.include_router(auth_router)
        return app

    def _create_main_server(self, app: FastAPI) -> Server:
        _config = Config(
            app,
            host="0.0.0.0",
            port=self.internal_server_port,
            log_level=config().log_level,
        )
        server = Server(_config)
        return server

    def _create_https_proxy_server(self) -> Optional[Server]:
        if not config().enable_local_callback_proxy:
            return None
        from hyperpocket.config.settings import POCKET_ROOT
        from hyperpocket.server.proxy import _generate_ssl_certificates, https_proxy_app

        ssl_keypath = POCKET_ROOT / "callback_server.key"
        ssl_certpath = POCKET_ROOT / "callback_server.crt"

        if not ssl_keypath.exists() or not ssl_certpath.exists():
            _generate_ssl_certificates(ssl_keypath, ssl_certpath)

        _config = Config(
            https_proxy_app,
            host="0.0.0.0",
            port=self.proxy_port,
            ssl_keyfile=ssl_keypath,
            ssl_certfile=ssl_certpath,
            log_level=config().log_level,
        )
        proxy_server = Server(_config)
        return proxy_server
