from unittest.async_case import IsolatedAsyncioTestCase
from urllib.parse import urlparse, parse_qs

from hyperpocket.auth.slack.token_context import SlackTokenAuthContext
from hyperpocket.auth.slack.token_handler import SlackTokenAuthHandler
from hyperpocket.auth.slack.token_schema import SlackTokenRequest
from hyperpocket.futures import FutureStore


class TestSlackTokenAuthHandler(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.handler: SlackTokenAuthHandler = SlackTokenAuthHandler()
        self.auth_req = SlackTokenRequest()

    async def test_make_auth_url(self):
        auth_url = self.handler._make_auth_url(
            req=self.auth_req,
            redirect_uri="http://test-redirect-uri.com",
            state="test-future-id"
        )
        parsed = urlparse(auth_url)
        query_params = parse_qs(parsed.query)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        # then
        self.assertEqual(base_url, self.handler._TOKEN_URL)
        self.assertEqual(query_params["state"][0], "test-future-id")
        self.assertEqual(query_params["redirect_uri"][0], "http://test-redirect-uri.com")

    async def test_prepare(self):
        # when
        prepare: str = self.handler.prepare(
            auth_req=self.auth_req,
            thread_id="test-prepare-thread-id",
            profile="test-prepare-profile",
            future_uid="test-prepare-future-uid",
        )
        auth_url = prepare.removeprefix("User needs to authenticate using the following URL:").strip()
        future_data = FutureStore.get_future( uid="test-prepare-future-uid")

        # then
        self.assertTrue(auth_url.startswith(self.handler._TOKEN_URL))
        self.assertIsNotNone(future_data)
        self.assertEqual(future_data.data["thread_id"], "test-prepare-thread-id")
        self.assertEqual(future_data.data["profile"], "test-prepare-profile")
        self.assertFalse(future_data.future.done())

    async def test_authenticate(self):
        self.handler.prepare(
            auth_req=self.auth_req,
            thread_id="test-thread-id",
            profile="test-profile",
            future_uid="test-future-uid"
        )
        future_data = FutureStore.get_future( uid="test-future-uid")
        future_data.future.set_result("test-token")

        response: SlackTokenAuthContext = await self.handler.authenticate(
            auth_req=self.auth_req,
            future_uid="test-future-uid"
        )

        self.assertIsInstance(response, SlackTokenAuthContext)
        self.assertEqual(response.access_token, "test-token")
        self.assertIsNone(response.expires_at)
