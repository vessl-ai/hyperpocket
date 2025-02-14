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


class PocketServerOperations(enum.Enum):
    CALL = "call"
    PREPARE_AUTH = "prepare_auth"
    AUTHENTICATE = "authenticate"
    TOOL_CALL = "tool_call"
    PLUG_CORE = "plug_core"


class PocketServer(object):
    fastapi_app: Optional[FastAPI]
    main_server: Optional[Server]
    internal_server_port: int
    proxy_server: Optional[Server]
    proxy_port: int
    pipe: mp.Pipe
    process: mp.Process
    future_store: dict[str, asyncio.Future]
    torn_down: bool = False
    _uidset: set
    _cores: dict[str, PocketCore]

    def __init__(self):
        self._initialized = False
        self.internal_server_port = config().internal_server_port
        self.proxy_port = config().public_server_port
        self._uidset = set()
        self.future_store = dict()
        self.fastapi_app = None
        self.main_server = None
        self._cores = dict()

    # should be called in child process
    def _plug_core(self, pocket_uid: str, pocket_core: PocketCore, *_a, **_kw):
        # extend http routers from each docks
        dock_routes = set([str(r) for r in self.fastapi_app.routes])

        for dock in pocket_core.docks:
            # check duplicated api route
            dock_route = set([str(r) for r in dock.router.routes])
            if dock_route in dock_routes:
                continue

            dock_routes.update(dock_route)
            self.fastapi_app.include_router(dock.router)

        # keep pocket core
        self._cores[pocket_uid] = pocket_core

    # should be called in parent process
    async def plug_core(self, pocket_uid: str, pocket_core: PocketCore):
        await self.call_in_subprocess(
            PocketServerOperations.PLUG_CORE,
            pocket_uid,
            tuple(),
            {
                "pocket_uid": pocket_uid,
                "pocket_core": pocket_core,
            },
        )

    @classmethod
    def get_instance_and_refcnt_up(cls, uid: str):
        if cls.__dict__.get("_instance") is None:
            cls._instance = cls()
            cls._instance.run()
        cls._instance.refcnt_up(uid)
        return cls._instance

    def refcnt_up(self, uid: str):
        self._uidset.add(uid)

    def refcnt_down(self, uid: str):
        if uid in self._uidset:
            self._uidset.remove(uid)
            if len(self._uidset) == 0:
                self._instance.teardown()

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

        async def _acall(_conn, _future_uid, _core_uid, _args, _kwargs):
            try:
                core = self._cores[_core_uid]
                result = await core.acall(*_args, **_kwargs)
                error = None
            except Exception as e:
                pocket_logger.error(f"failed in pocket subprocess. error: {e}")
                result = None
                error = e
            _conn.send((_future_uid, result, error))

        async def _prepare(_conn, _future_uid, _core_uid, a, kw):
            try:
                core = self._cores[_core_uid]
                result = core.prepare_auth(*a, **kw)
                error = None
            except Exception as e:
                pocket_logger.error(
                    f"failed to prepare in pocket subprocess. error: {e}"
                )
                result = None
                error = e

            _conn.send((_future_uid, result, error))

        async def _authenticate(_conn, _future_uid, _core_uid, a, kw):
            try:
                core = self._cores[_core_uid]
                result = await core.authenticate(*a, **kw)
                error = None
            except Exception as e:
                pocket_logger.error(
                    f"failed to authenticate in pocket subprocess. error: {e}"
                )
                result = None
                error = e

            _conn.send((_future_uid, result, error))

        async def _tool_call(_conn, _future_uid, _core_uid, a, kw):
            try:
                core = self._cores[_core_uid]
                result = await core.tool_call(*a, **kw)
                error = None
            except Exception as e:
                pocket_logger.error(
                    f"failed to tool_call in pocket subprocess. error: {e}"
                )
                result = None
                error = e

            _conn.send((_future_uid, result, error))

        async def _plug_core(_conn, _future_uid, _core_uid, a, kw):
            try:
                self._plug_core(*a, **kw)
                _conn.send((_future_uid, None, None))
            except Exception as e:
                pocket_logger.error(
                    f"failed to plug_core in pocket subprocess. error: {e}"
                )
                _conn.send((_future_uid, None, e))

        while True:
            if conn.poll():
                op, future_uid, core_uid, args, kwargs = conn.recv()
                if op == PocketServerOperations.CALL:
                    loop.create_task(_acall(conn, future_uid, core_uid, args, kwargs))
                elif op == PocketServerOperations.PREPARE_AUTH:
                    loop.create_task(_prepare(conn, future_uid, core_uid, args, kwargs))
                elif op == PocketServerOperations.AUTHENTICATE:
                    loop.create_task(_authenticate(conn, future_uid, core_uid, args, kwargs))
                elif op == PocketServerOperations.TOOL_CALL:
                    loop.create_task(_tool_call(conn, future_uid, core_uid, args, kwargs))
                elif op == PocketServerOperations.PLUG_CORE:
                    loop.create_task(_plug_core(conn, future_uid, core_uid, args, kwargs))
                else:
                    raise ValueError(f"Unknown operation: {op}")
            else:
                await asyncio.sleep(0)

    def send_in_parent(self, op: PocketServerOperations, pocket_uid: str, args: tuple, kwargs: dict):
        conn, _ = self.pipe
        future_uid = str(uuid.uuid4())
        message = (op, future_uid, pocket_uid, args, kwargs)
        future = asyncio.Future()
        self.future_store[future_uid] = future
        conn.send(message)
        return future_uid

    async def poll_in_parent(self):
        conn, _ = self.pipe
        while True:
            if conn.poll():
                uid, result, error = conn.recv()
                future = self.future_store[uid]
                if error:
                    future.set_exception(error)
                else:
                    future.set_result(result)
                break
            else:
                await asyncio.sleep(0)

    async def call_in_subprocess(
        self, op: PocketServerOperations, pocket_uid: str, args: tuple, kwargs: dict
    ):
        uid = self.send_in_parent(op, pocket_uid, args, kwargs)
        loop = asyncio.get_running_loop()
        loop.create_task(self.poll_in_parent())
        return await self.future_store[uid]

    def run(self):
        self._set_mp_start_method()

        error_queue = mp.Queue()
        self.pipe = mp.Pipe()
        self.process = mp.Process(
            target=self._run
        )
        self.process.start()  # process start

        if not error_queue.empty():
            error_message = error_queue.get()
            raise error_message

    def _report_initialized(self, error: Optional[Exception] = None):
        _, conn = self.pipe
        conn.send(('server-initialization', error,))

    def wait_initialized(self):
        if self._initialized:
            return
        conn, _ = self.pipe
        while True:
            if conn.poll():
                _, error = conn.recv()
                if error:
                    raise error
                break
        self._initialized = True

    def _run(self):
        try:
            # init process
            self.fastapi_app = self._create_fastapi_app()
            self.main_server = self._create_main_server(self.fastapi_app)
            self.proxy_server = self._create_https_proxy_server()
            self._report_initialized()

            loop = asyncio.new_event_loop()
            loop.run_until_complete(self._run_async())
            loop.close()
        except Exception as error:
            self._report_initialized(error)

    def _create_fastapi_app(self) -> FastAPI:
        app = FastAPI()
        app.include_router(auth_router)
        app.add_api_route("/health", lambda: {"status": "ok"}, methods=["GET"])
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
