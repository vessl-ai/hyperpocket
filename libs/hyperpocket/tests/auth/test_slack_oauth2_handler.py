import uuid
from datetime import datetime, timezone
from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import httpx

from hyperpocket.auth.slack.oauth2_context import SlackOAuth2AuthContext
from hyperpocket.auth.slack.oauth2_handler import SlackOAuth2AuthHandler
from hyperpocket.auth.slack.oauth2_schema import SlackOAuth2Request, SlackOAuth2Response
from hyperpocket.config import config
from hyperpocket.config.auth import SlackAuthConfig
from hyperpocket.futures import FutureStore


class TestSlackOAuth2AuthHandler(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        config().auth.slack = SlackAuthConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
        )

        self.handler = SlackOAuth2AuthHandler()
        self.auth_req = SlackOAuth2Request(
            auth_scopes=[
                "channels:history",
                "im:history",
                "mpim:history",
                "groups:history",
                "reactions:read",
            ],
            client_id="test-client-id",
            client_secret="test-client-secret",
        )

    async def test_make_auth_url(self):
        future_uid = str(uuid.uuid4())

        auth_url = self.handler._make_auth_url(
            req=self.auth_req,
            redirect_uri="http://test-redirect-uri.com",
            state=future_uid,
        )
        parsed = urlparse(auth_url)
        query_params = parse_qs(parsed.query)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        # then
        self.assertEqual(base_url, SlackOAuth2AuthHandler._SLACK_OAUTH_URL)
        self.assertEqual(query_params["state"][0], future_uid)
        self.assertEqual(
            query_params["redirect_uri"][0], "http://test-redirect-uri.com"
        )
        self.assertEqual(query_params["client_id"][0], "test-client-id")
        self.assertEqual(
            query_params["user_scope"][0],
            "channels:history,im:history,mpim:history,groups:history,reactions:read",
        )

    async def test_prepare(self):
        future_uid = str(uuid.uuid4())

        # when
        prepare: str = self.handler.prepare(
            auth_req=self.auth_req,
            thread_id="test-prepare-thread-id",
            profile="test-prepare-profile",
            future_uid=future_uid,
        )
        auth_url = prepare.removeprefix(
            "User needs to authenticate using the following URL:"
        ).strip()
        future_data = FutureStore.get_future(uid=future_uid)

        # then
        self.assertTrue(auth_url.startswith(SlackOAuth2AuthHandler._SLACK_OAUTH_URL))
        self.assertIsNotNone(future_data)
        self.assertEqual(future_data.data["thread_id"], "test-prepare-thread-id")
        self.assertEqual(future_data.data["profile"], "test-prepare-profile")
        self.assertFalse(future_data.future.done())

    async def test_authenticate(self):
        # given
        future_uid = str(uuid.uuid4())
        mock_response = httpx.Response(
            status_code=200,
            json={
                "ok": True,
                "authed_user": {"id": "test-user", "access_token": "test-token"},
            },
        )

        # when
        self.handler.prepare(
            auth_req=self.auth_req,
            thread_id="test-thread-id",
            profile="test-profile",
            future_uid=future_uid,
        )
        future_data = FutureStore.get_future(uid=future_uid)
        future_data.future.set_result("test-code")

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            response = await self.handler.authenticate(
                auth_req=self.auth_req, future_uid=future_uid
            )

        self.assertIsInstance(response, SlackOAuth2AuthContext)
        self.assertEqual(response.access_token, "test-token")

    async def test_refresh(self):
        # given
        # https://api.slack.com/authentication/rotation
        mock_response = httpx.Response(
            status_code=200,
            json={
                "ok": True,
                "access_token": "new-access-token",
                "refresh_token": "new-refresh-token",
                "expires_in": 3600,
            },
        )

        response = SlackOAuth2Response(
            **{
                "ok": True,
                "authed_user": {
                    "id": "test",
                    "access_token": "access-token",
                    "refresh_token": "refresh-token",
                    "expires_in": 3600,
                },
            }
        )
        context = SlackOAuth2AuthContext.from_slack_oauth2_response(response)

        # when
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            new_context: SlackOAuth2AuthContext = await self.handler.refresh(
                auth_req=self.auth_req, context=context
            )

        time_diff = new_context.expires_at - datetime.now(tz=timezone.utc)

        # then
        self.assertIsInstance(new_context, SlackOAuth2AuthContext)
        self.assertEqual(context.access_token, "access-token")
        self.assertEqual(context.refresh_token, "refresh-token")
        self.assertEqual(new_context.access_token, "new-access-token")
        self.assertEqual(new_context.refresh_token, "new-refresh-token")
        self.assertTrue(time_diff.total_seconds() > 3500)
