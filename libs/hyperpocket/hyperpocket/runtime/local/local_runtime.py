import asyncio
from typing import Coroutine

import multiprocess

from hyperpocket.runtime.runtime import Runtime


class LocalRuntime(Runtime):
    def run(self, func, args, envs):
        pipe = multiprocess.Pipe()
        process = multiprocess.Process(
            target=self._run,
            args=(func, args, envs, pipe),
        )
        process.start()
        conn, _ = pipe
        while True:
            if conn.poll():
                result = conn.recv()
                break
        process.terminate()
        process.join()
        return result

    def _run(self, func, args, envs, pipe: multiprocess.Pipe):
        import os

        for key, value in envs.items():
            os.environ[key] = value

        result = func(**args)
        if isinstance(result, Coroutine):
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(result)
        _, conn = pipe
        conn.send(result)
