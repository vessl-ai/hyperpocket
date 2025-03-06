import asyncio
from typing import Any

from hyperpocket.config import pocket_logger


class FutureData:
    future: asyncio.Future
    data: dict

    def __init__(self, future: asyncio.Future, data: dict):
        self.future = future
        self.data = data


class FutureStore(object):
    futures: dict[str, FutureData]

    def __init__(self):
        self.futures = dict()

    def create_future(self, uid: str, data: dict = None) -> FutureData:
        if future := self.get_future(uid) is not None:
            pocket_logger.info(
                f"the future already exists. the existing future is returned. uid: {uid}"
            )
            return future
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        future_data = FutureData(future=future, data=data)

        self.futures[uid] = future_data

        return future_data

    def get_future(self, uid: str) -> FutureData:
        return self.futures.get(uid, None)

    def resolve_future(self, uid: str, value: Any):
        future_data = self.futures.get(uid)
        if not future_data:
            raise ValueError(f"Future not found for uid={uid}")
        if not future_data.future.done():
            # if the future loop is running, it should be executed in same event loop
            loop = future_data.future.get_loop()
            if loop.is_running():
                loop.call_soon_threadsafe(future_data.future.set_result, value)
            # if the future loop is not running, it can be executed from anywhere.
            else:
                future_data.future.set_result(value)

    def delete_future(self, uid: str):
        self.futures.pop(uid, None)
