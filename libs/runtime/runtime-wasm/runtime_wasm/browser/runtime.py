from typing import Optional

from runtime_wasm.browser.invoker import Invoker
from runtime_wasm.browser.invoker_browser import InvokerBrowser
from runtime_wasm.runtime import WasmRuntime


class BrowserScriptRuntime(WasmRuntime):
    _browser: Optional[InvokerBrowser]
    _invoker: Optional[Invoker]

    def __init__(self):
        self._browser = None
        self._invoker = None

    async def invoker(self) -> Invoker:
        if self._invoker is None:
            self._browser = await InvokerBrowser.async_init()
            self._invoker = Invoker(self._browser)
        return self._invoker

    async def teardown(self):
        if self._browser is not None:
            await self._browser.teardown()

    async def ainvoke(self, *args, **kwargs):
        invoker = await self.invoker()
        return await invoker.ainvoke(*args, **kwargs)
