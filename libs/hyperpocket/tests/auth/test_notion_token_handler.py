from unittest.async_case import IsolatedAsyncioTestCase
from urllib.parse import parse_qs, urlparse

from hyperpocket.auth.notion.token_context import NotionTokenAuthContext
from hyperpocket.auth.notion.token_handler import NotionTokenAuthHandler
from hyperpocket.auth.notion.token_schema import NotionTokenRequest
from hyperpocket.futures import FutureStore


class TestNotionTokenAuthHandler(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.handler: NotionTokenAuthHandler = NotionTokenAuthHandler()
        self.auth_req = NotionTokenRequest()

    async def test_make_auth_url(self):
        auth_url = self.handler._make_auth_url(
            auth_req=self.auth_req,
            redirect_uri="http://test-notion-redirect-uri.com",
            state="test-notion-future-id",
        )
        parsed = urlparse(auth_url)
        query_params = parse_qs(parsed.query)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        # then
        self.assertEqual(base_url, self.handler._TOKEN_URL)
        self.assertEqual(query_params["state"][0], "test-notion-future-id")
        self.assertEqual(
            query_params["redirect_uri"][0], "http://test-notion-redirect-uri.com"
        )

    async def test_prepare(self):
        # when
        prepare: str = self.handler.prepare(
            auth_req=self.auth_req,
            thread_id="test-notion-prepare-thread-id",
            profile="test-notion-prepare-profile",
            future_uid="test-notion-prepare-future-uid",
        )
        auth_url = prepare.removeprefix(
            "User needs to authenticate using the following URL:"
        ).strip()
        future_data = FutureStore.get_future(uid="test-notion-prepare-future-uid")

        # then
        self.assertTrue(auth_url.startswith(self.handler._TOKEN_URL))
        self.assertIsNotNone(future_data)
        self.assertEqual(future_data.data["thread_id"], "test-notion-prepare-thread-id")
        self.assertEqual(future_data.data["profile"], "test-notion-prepare-profile")
        self.assertFalse(future_data.future.done())

    async def test_authenticate(self):
        self.handler.prepare(
            auth_req=self.auth_req,
            thread_id="test-notion-thread-id",
            profile="test-notion-profile",
            future_uid="test-notion-future-uid",
        )
        future_data = FutureStore.get_future(uid="test-notion-future-uid")
        future_data.future.set_result("test-notion-token")

        response: NotionTokenAuthContext = await self.handler.authenticate(
            auth_req=self.auth_req, future_uid="test-notion-future-uid"
        )

        self.assertIsInstance(response, NotionTokenAuthContext)
        self.assertEqual(response.access_token, "test-notion-token")
        self.assertIsNone(response.expires_at)
