from playwright.async_api import (
    BrowserContext,
    Page,
    Playwright,
    Route,
    async_playwright,
)


class InvokerBrowser(object):
    playwright: Playwright
    browser_context: BrowserContext

    @classmethod
    async def async_init(cls):
        instance = cls()
        instance.playwright = await async_playwright().start()
        instance.browser_context = await instance.playwright.chromium.launch_persistent_context(
            headless=True,
            args=[
                "--disable-web-security=True",
            ],
            user_data_dir="/tmp/chrome_dev_user",
        )
        return instance

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
