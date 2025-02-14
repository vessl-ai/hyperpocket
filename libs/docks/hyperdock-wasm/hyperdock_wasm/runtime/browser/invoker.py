import asyncio
import json
import uuid
from typing import Any
from urllib.parse import urljoin

from hyperpocket.config import config
from hyperpocket.futures import FutureStore
from hyperdock_wasm.runtime.browser.invoker_browser import InvokerBrowser
from hyperdock_wasm.runtime.browser.script import Script, ScriptRuntime, ScriptStore
from hyperdock_wasm.runtime.browser.templates import render


class Invoker(object):
    browser: InvokerBrowser

    def __init__(self, browser: InvokerBrowser):
        self.browser = browser

    def invoke(
        self, tool_path: str, runtime: ScriptRuntime, body: Any, envs: dict, **kwargs
    ) -> str:
        try:
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(
                self.ainvoke(tool_path, runtime, body, envs, **kwargs)
            )
        except RuntimeError:
            asyncio.run(self.ainvoke(tool_path, runtime, body, envs, **kwargs))
        except Exception as e:
            return "There was an error while executing the tool: " + str(e)

    async def ainvoke(
        self, tool_path: str, runtime: ScriptRuntime, body: Any, envs: dict, **kwargs
    ) -> str:
        script_future_uid = str(uuid.uuid4())
        html = render(runtime.value, script_future_uid, envs, json.dumps(body))
        script = Script(
            id=script_future_uid, tool_path=tool_path, rendered_html=html, runtime=runtime
        )
        ScriptStore.add_script(script=script)
        future_data = FutureStore.create_future(uid=script_future_uid)
        page = await self.browser.new_page()
        url = urljoin(
            config().internal_base_url + "/", f"scripts/{script_future_uid}/browse"
        )
        await page.goto(url)
        stdout = await future_data.future
        await page.close()
        return stdout
