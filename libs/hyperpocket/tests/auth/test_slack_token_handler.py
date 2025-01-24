from unittest.async_case import IsolatedAsyncioTestCase
from urllib.parse import parse_qs, urlparse

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
            redirect_uri="http://test-slack-redirect-uri.com",
            state="test-slack-future-id",
        )
        parsed = urlparse(auth_url)
        query_params = parse_qs(parsed.query)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        # then
        self.assertEqual(base_url, self.handler._TOKEN_URL)
        self.assertEqual(query_params["state"][0], "test-slack-future-id")
        self.assertEqual(
            query_params["redirect_uri"][0], "http://test-slack-redirect-uri.com"
        )

    async def test_prepare(self):
        # when
        prepare: str = self.handler.prepare(
            auth_req=self.auth_req,
            thread_id="test-slack-prepare-thread-id",
            profile="test-slack-prepare-profile",
            future_uid="test-slack-prepare-future-uid",
        )
        auth_url = prepare.removeprefix(
            "User needs to authenticate using the following URL:"
        ).strip()
        future_data = FutureStore.get_future(uid="test-slack-prepare-future-uid")

        # then
        self.assertTrue(auth_url.startswith(self.handler._TOKEN_URL))
        self.assertIsNotNone(future_data)
        self.assertEqual(future_data.data["thread_id"], "test-slack-prepare-thread-id")
        self.assertEqual(future_data.data["profile"], "test-slack-prepare-profile")
        self.assertFalse(future_data.future.done())

    async def test_authenticate(self):
        self.handler.prepare(
            auth_req=self.auth_req,
            thread_id="test-slack-thread-id",
            profile="test-slack-profile",
            future_uid="test-slack-future-uid",
        )
        future_data = FutureStore.get_future(uid="test-slack-future-uid")
        future_data.future.set_result("test-slack-token")

        response: SlackTokenAuthContext = await self.handler.authenticate(
            auth_req=self.auth_req, future_uid="test-slack-future-uid"
        )

        self.assertIsInstance(response, SlackTokenAuthContext)
        self.assertEqual(response.access_token, "test-slack-token")
        self.assertIsNone(response.expires_at)
