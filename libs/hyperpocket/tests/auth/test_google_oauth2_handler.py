import uuid
from datetime import datetime, timezone
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import httpx

from hyperpocket.auth.google.oauth2_context import GoogleOAuth2AuthContext
from hyperpocket.auth.google.oauth2_handler import GoogleOAuth2AuthHandler
from hyperpocket.auth.google.oauth2_schema import (
    GoogleOAuth2Request,
    GoogleOAuth2Response,
)
from hyperpocket.config import config
from hyperpocket.config.auth import GoogleAuthConfig
from hyperpocket.futures import FutureStore


class TestGoogleOAuth2AuthHandler(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        config().auth.google = GoogleAuthConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
        )

        self.handler = GoogleOAuth2AuthHandler()
        self.auth_req = GoogleOAuth2Request(
            auth_scopes=["https://www.googleapis.com/auth/calendar"],
            client_id="test-client-id",
            client_secret="test-client-secret",
        )

    async def test_make_auth_url(self):
        future_uid = str(uuid.uuid4())

        auth_url = self.handler._make_auth_url(
            auth_req=self.auth_req,
            redirect_uri="http://test-redirect-uri.com",
            state=future_uid,
        )
        parsed = urlparse(auth_url)
        query_params = parse_qs(parsed.query)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        # then
        self.assertEqual(base_url, self.handler._GOOGLE_AUTH_URL)
        self.assertEqual(query_params["state"][0], future_uid)
        self.assertEqual(
            query_params["redirect_uri"][0], "http://test-redirect-uri.com"
        )
        self.assertEqual(query_params["client_id"][0], "test-client-id")
        self.assertEqual(
            query_params["scope"][0], "https://www.googleapis.com/auth/calendar"
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
        self.assertTrue(auth_url.startswith(self.handler._GOOGLE_AUTH_URL))
        self.assertIsNotNone(future_data)
        self.assertEqual(future_data.data["thread_id"], "test-prepare-thread-id")
        self.assertEqual(future_data.data["profile"], "test-prepare-profile")
        self.assertFalse(future_data.future.done())

    async def test_authenticate(self):
        mock_response = httpx.Response(
            status_code=200,
            json={
                "access_token": "test-token",
                "refresh_token": "test-refresh-token",
                "expires_in": 3600,
                "scope": "https://www.googleapis.com/auth/calendar",
                "token_type": "Bearer",
            },
        )
        future_uid = str(uuid.uuid4())

        self.handler.prepare(
            auth_req=self.auth_req,
            thread_id="test-thread-id",
            profile="test-profile",
            future_uid=future_uid,
        )
        future_data = FutureStore.get_future(uid=future_uid)
        future_data.future.set_result("test-code")

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            response: GoogleOAuth2AuthContext = await self.handler.authenticate(
                auth_req=self.auth_req, future_uid=future_uid
            )

        time_diff = (
            response.expires_at - datetime.now(tz=timezone.utc)
        ).total_seconds()

        self.assertIsInstance(response, GoogleOAuth2AuthContext)
        self.assertEqual(response.access_token, "test-token")
        self.assertEqual(response.refresh_token, "test-refresh-token")
        self.assertTrue(time_diff > 3500)

    async def test_refresh(self):
        # given
        mock_response = httpx.Response(
            status_code=200,
            json={
                "access_token": "new-test-token",
                "expires_in": 3600,
                "scope": "https://www.googleapis.com/auth/calendar",
                "token_type": "Bearer",
            },
        )
        response = GoogleOAuth2Response(
            **{
                "access_token": "test-token",
                "expires_in": 100,
                "scope": "https://www.googleapis.com/auth/calendar",
                "refresh_token": "test-refresh-token",
                "token_type": "Bearer",
            }
        )
        context = GoogleOAuth2AuthContext.from_google_oauth2_response(response)

        # when
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            new_context: GoogleOAuth2AuthContext = await self.handler.refresh(
                auth_req=self.auth_req, context=context
            )

        old_time_diff = context.expires_at - datetime.now(tz=timezone.utc)
        new_time_diff = new_context.expires_at - datetime.now(tz=timezone.utc)

        # then
        self.assertIsInstance(new_context, GoogleOAuth2AuthContext)
        self.assertEqual(context.access_token, "test-token")
        self.assertEqual(context.refresh_token, "test-refresh-token")
        self.assertTrue(old_time_diff.total_seconds() < 100)

        self.assertEqual(new_context.access_token, "new-test-token")
        self.assertEqual(new_context.refresh_token, "test-refresh-token")
        self.assertTrue(new_time_diff.total_seconds() > 3500)
