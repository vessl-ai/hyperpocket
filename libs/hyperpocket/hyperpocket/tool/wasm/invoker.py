import asyncio
import json
import uuid
from typing import Any
from urllib.parse import urljoin

from hyperpocket.config import config
from hyperpocket.futures import FutureStore
from hyperpocket.tool.wasm.browser import InvokerBrowser
from hyperpocket.tool.wasm.script import Script, ScriptRuntime, ScriptStore
from hyperpocket.tool.wasm.templates import render


class WasmInvoker(object):
    def invoke(
        self, tool_path: str, runtime: ScriptRuntime, body: Any, envs: dict, **kwargs
    ) -> str:
        loop = asyncio.get_running_loop()
        return loop.run_until_complete(
            self.ainvoke(tool_path, runtime, body, envs, **kwargs)
        )

    async def ainvoke(
        self, tool_path: str, runtime: ScriptRuntime, body: Any, envs: dict, **kwargs
    ) -> str:
        uid = str(uuid.uuid4())
        html = render(runtime.value, uid, envs, json.dumps(body))
        script = Script(
            id=uid, tool_path=tool_path, rendered_html=html, runtime=runtime
        )
        ScriptStore.add_script(script=script)
        future_data = FutureStore.create_future(uid=uid)
        browser = await InvokerBrowser.get_instance()
        page = await browser.new_page()
        url = urljoin(
            config().internal_base_url + "/", f"tools/wasm/scripts/{uid}/browse"
        )
        await page.goto(url)
        stdout = await future_data.future
        await page.close()
        return stdout
