import asyncio
import enum
import uuid
from typing import Optional

import multiprocess as mp
from fastapi import FastAPI
from uvicorn import Config, Server

from hyperpocket.config import config, pocket_logger
from hyperpocket.pocket_core import PocketCore
from hyperpocket.server.auth import auth_router
from hyperpocket.server.tool import tool_router


class PocketServerOperations(enum.Enum):
    CALL = "call"
    PREPARE_AUTH = "prepare_auth"
    AUTHENTICATE = "authenticate"
    TOOL_CALL = "tool_call"


class PocketServer(object):
    main_server: Server
    internal_server_port: int
    proxy_server: Optional[Server]
    proxy_port: int
    pipe: mp.Pipe
    process: mp.Process
    future_store: dict[str, asyncio.Future]
    torn_down: bool = False

    def __init__(
        self,
        internal_server_port: int = config().internal_server_port,
        proxy_port: int = config().public_server_port,
    ):
        self.internal_server_port = internal_server_port
        self.proxy_port = proxy_port
        self.future_store = dict()

    def teardown(self):
        # @XXX(seokju) is it ok to call this method both in __del__ and __exit__?
        if self.torn_down:
            return
        self.torn_down = True
        self.process.terminate()
        self.process.join()

    async def _run_async(self):
        try:
            await asyncio.gather(
                self.main_server.serve(),
                self.proxy_server.serve()
                if self.proxy_server is not None
                else asyncio.sleep(0),
                self.poll_in_child(),
            )
        except Exception as e:
            pocket_logger.warning(f"failed to start pocket server. error : {e}")

    async def poll_in_child(self):
        loop = asyncio.get_running_loop()
        _, conn = self.pipe

        async def _acall(_conn, _op, _uid, a, kw):
            try:
                result = await self.pocket_core.acall(*a, **kw)
                error = None
            except Exception as e:
                pocket_logger.error(f"failed to acall in pocket subprocess. error: {e}")
                result = None
                error = e

            _conn.send((_op, _uid, result, error))

        async def _prepare(_conn, _op, _uid, a, kw):
            try:
                result = self.pocket_core.prepare_auth(*a, **kw)
                error = None
            except Exception as e:
                pocket_logger.error(
                    f"failed to prepare in pocket subprocess. error: {e}"
                )
                result = None
                error = e

            _conn.send((_op, _uid, result, error))

        async def _authenticate(_conn, _op, _uid, a, kw):
            try:
                result = await self.pocket_core.authenticate(*a, **kw)
                error = None
            except Exception as e:
                pocket_logger.error(
                    f"failed to authenticate in pocket subprocess. error: {e}"
                )
                result = None
                error = e

            _conn.send((_op, _uid, result, error))

        async def _tool_call(_conn, _op, _uid, a, kw):
            try:
                result = await self.pocket_core.tool_call(*a, **kw)
                error = None
            except Exception as e:
                pocket_logger.error(
                    f"failed to tool_call in pocket subprocess. error: {e}"
                )
                result = None
                error = e

            _conn.send((_op, _uid, result, error))

        while True:
            if conn.poll():
                op, uid, args, kwargs = conn.recv()
                if op == PocketServerOperations.CALL.value:
                    loop.create_task(_acall(conn, op, uid, args, kwargs))
                elif op == PocketServerOperations.PREPARE_AUTH.value:
                    loop.create_task(_prepare(conn, op, uid, args, kwargs))
                elif op == PocketServerOperations.AUTHENTICATE.value:
                    loop.create_task(_authenticate(conn, op, uid, args, kwargs))
                elif op == PocketServerOperations.TOOL_CALL.value:
                    loop.create_task(_tool_call(conn, op, uid, args, kwargs))
                else:
                    raise AttributeError(f"Can't find operations. op:{op}")
            else:
                await asyncio.sleep(0)

    def send_in_parent(self, op: PocketServerOperations, args: tuple, kwargs: dict):
        conn, _ = self.pipe
        uid = str(uuid.uuid4())
        message = (op.value, uid, args, kwargs)
        future = asyncio.Future()
        self.future_store[uid] = future
        conn.send(message)
        return uid

    async def poll_in_parent(self):
        conn, _ = self.pipe
        while True:
            if conn.poll():
                op, uid, result, error = conn.recv()
                future = self.future_store[uid]
                if error:
                    future.set_exception(error)
                else:
                    future.set_result(result)
                break
            else:
                await asyncio.sleep(0)

    async def call_in_subprocess(
        self, op: PocketServerOperations, args: tuple, kwargs: dict
    ):
        uid = self.send_in_parent(op, args, kwargs)
        loop = asyncio.get_running_loop()
        loop.create_task(self.poll_in_parent())
        return await self.future_store[uid]

    def run(self, pocket_core: PocketCore):
        self._set_mp_start_method()

        error_queue = mp.Queue()
        self.pipe = mp.Pipe()
        self.process = mp.Process(
            target=self._run, args=(pocket_core, )
        )
        self.process.start()  # process start

        if not error_queue.empty():
            error_message = error_queue.get()
            raise error_message
    
    def _report_initialized(self, error: Optional[Exception] = None):
        _, conn = self.pipe
        conn.send(('server-initialization', error,))
    
    def wait_initialized(self):
        conn, _ = self.pipe
        while True:
            if conn.poll():
                _, error = conn.recv()
                if error:
                    raise error
                return

    def _run(self, pocket_core):
        try:
            # init process
            self.pocket_core = pocket_core
            self.main_server = self._create_main_server()
            self.proxy_server = self._create_https_proxy_server()
            self._report_initialized()

            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._run_async())
            loop.close()
        except Exception as error:
            self._report_initialized(error)

    def _create_main_server(self) -> Server:
        app = FastAPI()
        _config = Config(
            app,
            host="0.0.0.0",
            port=self.internal_server_port,
            log_level=config().log_level,
        )
        app.include_router(tool_router)
        app.include_router(auth_router)
        app.add_api_route("/health", lambda: {"status": "ok"}, methods=["GET"])

        app = Server(_config)
        return app

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

    def _set_mp_start_method(self):
        import platform

        os_name = platform.system()
        if os_name == "Windows":
            mp.set_start_method("spawn", force=True)
            pocket_logger.debug("Process start method set to 'spawn' for Windows.")
        elif os_name == "Darwin":  # macOS
            mp.set_start_method("spawn", force=True)
            pocket_logger.debug("Process start method set to 'spawn' for macOS.")
        elif os_name == "Linux":
            mp.set_start_method("fork", force=True)
            pocket_logger.debug("Process start method set to 'fork' for Linux.")
        else:
            pocket_logger.debug(
                f"Unrecognized OS: {os_name}. Default start method will be used."
            )
