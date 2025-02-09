import asyncio

from playwright.async_api import (
    BrowserContext,
    Page,
    Playwright,
    Route,
    async_playwright,
)


class InvokerBrowser(object):
    _instance: "InvokerBrowser" = None
    _lock = asyncio.Lock()
    playwright: Playwright
    browser_context: BrowserContext

    def __init__(self):
        raise RuntimeError("Use InvokerBrowser.get_instance() instead")

    async def _async_init(self):
        self.playwright = await async_playwright().start()
        self.browser_context = await self.playwright.chromium.launch_persistent_context(
            headless=True,
            args=[
                "--disable-web-security=True",
            ],
            user_data_dir="/tmp/chrome_dev_user",
        )

    @classmethod
    async def get_instance(cls):
        if not cls._instance:
            async with cls._lock:
                if cls._instance is None:
                    instance = cls.__new__(cls)
                    await instance._async_init()
                    cls._instance = instance
        return cls._instance

    async def new_page(self) -> Page:
        page = await self.browser_context.new_page()

        async def _hijack_route(route: Route):
            response = await route.fetch()
            body = await response.body()
            await route.fulfill(
                response=response,
                body=body,
                headers={
                    **response.headers,
                    "Cross-Origin-Opener-Policy": "same-origin",
                    "Cross-Origin-Embedder-Policy": "require-corp",
                    "Cross-Origin-Resource-Policy": "cross-origin",
                },
            )

        await page.route("**/*", _hijack_route)
        return page

    async def teardown(self):
        await self.browser_context.close()
        await self.playwright.stop()
