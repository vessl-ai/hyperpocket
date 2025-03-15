import uuid
from datetime import datetime, timedelta, timezone
from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import patch

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.google.oauth2_context import GoogleOAuth2AuthContext
from hyperpocket.auth.google.oauth2_handler import GoogleOAuth2AuthHandler
from hyperpocket.auth.google.oauth2_schema import GoogleOAuth2Request
from hyperpocket.auth.slack.oauth2_context import SlackOAuth2AuthContext
from hyperpocket.config import config
from hyperpocket.config.auth import GoogleAuthConfig
from hyperpocket.config.session import SessionConfigInMemory
from hyperpocket.futures import FutureStore
from hyperpocket.pocket_auth import AuthState, PocketAuth
from hyperpocket.session.in_memory import InMemorySessionStorage


class TestPocketAuth(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.pocket_auth = PocketAuth(
            handlers=[GoogleOAuth2AuthHandler],
            session_storage=InMemorySessionStorage(SessionConfigInMemory()),
        )

        config().auth.google = GoogleAuthConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
        )

        self.thread_id = "default-thread-id"
        self.profile = "default-profile"
        self.auth_provider = AuthProvider.GOOGLE
        self.auth_handler_name = None
        self.scope = ["scope-1", "scope-2"]
        return

    async def asyncTearDown(self):
        InMemorySessionStorage.storage.clear()

    async def test_make_request(self):
        """
        Test that a GoogleOAuth2Request is correctly created with the specified auth scopes and provider.
        """
        request: GoogleOAuth2Request = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        self.assertIsInstance(request, GoogleOAuth2Request)
        self.assertEqual(request.auth_scopes, self.scope)

    async def test_create_pending_session(self):
        """
        Test that a pending session is created correctly,
        and that the session is in a pending state with the correct future UID and provider name.
        in pending state, the auth context doesn't be returned.
        """
        # given
        future_uid = str(uuid.uuid4())
        handler = self.pocket_auth.find_handler_instance(
            name=self.auth_handler_name, auth_provider=self.auth_provider
        )

        # when
        prev_context = self.pocket_auth.get_auth_context(
            AuthProvider.GOOGLE,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        session = self.pocket_auth._upsert_pending_session(
            auth_handler=handler,
            future_uid=future_uid,
            profile=self.profile,
            thread_id=self.thread_id,
            scope=set(self.scope),
        )

        after_context = self.pocket_auth.get_auth_context(
            AuthProvider.GOOGLE,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertIsNone(prev_context)
        self.assertIsNone(
            after_context
        )  # should be none even after creating session in pending session.
        self.assertIsNotNone(session)
        self.assertIsNone(session.auth_context)
        self.assertIsNotNone(session.auth_resolve_uid)
        self.assertEqual(session.auth_resolve_uid, future_uid)
        self.assertEqual(session.auth_provider_name, self.auth_provider.name)
        self.assertEqual(session.scoped, handler.scoped)

    async def test_set_session_active(self):
        """
        Test that a session is correctly set to active with a valid auth context.
        """
        # given
        future_uid = str(uuid.uuid4())
        handler = self.pocket_auth.find_handler_instance(
            name=self.auth_handler_name, auth_provider=self.auth_provider
        )

        # when
        before_session_pending = self.pocket_auth.get_auth_context(
            AuthProvider.GOOGLE,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        session = self.pocket_auth._upsert_pending_session(
            auth_handler=handler,
            future_uid=future_uid,
            profile=self.profile,
            thread_id=self.thread_id,
            scope=set(self.scope),
        )

        after_session_pending = self.pocket_auth.get_auth_context(
            AuthProvider.GOOGLE,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        await self.pocket_auth._set_session_active(
            context=GoogleOAuth2AuthContext(
                access_token="access-token",
                refresh_token="refresh-token",
                description="test-description",
                expires_at=datetime.now(tz=timezone.utc),
            ),
            provider=self.auth_provider,
            profile=self.profile,
            thread_id=self.thread_id,
        )

        after_session_active: GoogleOAuth2AuthContext = (
            self.pocket_auth.get_auth_context(
                AuthProvider.GOOGLE,
                thread_id=self.thread_id,
                profile=self.profile,
            )
        )

        # then
        self.assertIsNone(before_session_pending)

        self.assertIsNotNone(session)
        self.assertIsNone(
            session.auth_context
        )  # should be none even after creating session in pending session.
        self.assertIsNotNone(session.auth_resolve_uid)
        self.assertEqual(session.auth_resolve_uid, future_uid)

        # pending session's auth context is also none.
        self.assertIsNone(after_session_pending)

        # auth_context should not be none after activating session
        self.assertIsNotNone(after_session_active)
        self.assertEqual(after_session_active.access_token, "access-token")
        self.assertEqual(after_session_active.refresh_token, "refresh-token")
        self.assertEqual(after_session_active.description, "test-description")

    async def test_auth_check_no_session_case(self):
        """
        Test `PocketAuth.check` in the case where there is no session available.
        The auth state should be NO_SESSION.
        """
        # given
        auth_req: GoogleOAuth2Request = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        # when
        auth_state = await self.pocket_auth.check(
            auth_req=auth_req,
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(auth_state, AuthState.NO_SESSION)

    async def test_auth_check_pending_resolve_case(self):
        """
        Test `PocketAuth.check` in the case where the session is in a PENDING_RESOLVE state.
        The auth state should be PENDING_RESOLVE.
        """
        # given
        future_uid = str(uuid.uuid4())
        handler = self.pocket_auth.find_handler_instance(
            name=self.auth_handler_name, auth_provider=self.auth_provider
        )
        auth_req: GoogleOAuth2Request = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        # when
        self.pocket_auth._upsert_pending_session(
            auth_handler=handler,
            future_uid=future_uid,
            profile=self.profile,
            thread_id=self.thread_id,
            scope=set(self.scope),
        )

        auth_state = await self.pocket_auth.check(
            auth_req=auth_req,
            auth_provider=self.auth_provider,
            auth_handler_name=handler.name,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(auth_state, AuthState.PENDING_RESOLVE)

    async def test_auth_check_resolved_case(self):
        """
        Test `PocketAuth.check` in the case where the session is in a RESOLVED state.
        The auth state should be RESOLVED.
        """
        # given
        future_uid = str(uuid.uuid4())
        handler = self.pocket_auth.find_handler_instance(
            name=self.auth_handler_name, auth_provider=self.auth_provider
        )
        auth_req: GoogleOAuth2Request = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        # when
        future_data = FutureStore.create_future(uid=future_uid)
        self.pocket_auth._upsert_pending_session(
            auth_handler=handler,
            future_uid=future_uid,
            profile=self.profile,
            thread_id=self.thread_id,
            scope=set(self.scope),
        )

        future_data.future.set_result("test-code")
        auth_state = await self.pocket_auth.check(
            auth_req=auth_req,
            auth_provider=self.auth_provider,
            auth_handler_name=handler.name,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(auth_state, AuthState.RESOLVED)

    async def test_auth_check_skip_auth_case(self):
        """
        Test `PocketAuth.check` in the case where the pending session gets active and the auth context is set.
        The auth state should be SKIP_AUTH.
        """
        # given
        future_uid = str(uuid.uuid4())
        handler = self.pocket_auth.find_handler_instance(
            name=self.auth_handler_name, auth_provider=self.auth_provider
        )
        auth_req: GoogleOAuth2Request = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        # when
        # set pending session
        self.pocket_auth._upsert_pending_session(
            auth_handler=handler,
            future_uid=future_uid,
            profile=self.profile,
            thread_id=self.thread_id,
            scope=set(self.scope),
        )

        # activate session
        await self.pocket_auth._set_session_active(
            context=GoogleOAuth2AuthContext(
                access_token="access-token",
                refresh_token="refresh-token",
                description="test-description",
                expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=30),
            ),
            provider=self.auth_provider,
            profile=self.profile,
            thread_id=self.thread_id,
        )

        auth_state = await self.pocket_auth.check(
            auth_req=auth_req,
            auth_provider=self.auth_provider,
            auth_handler_name=handler.name,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(auth_state, AuthState.SKIP_AUTH)

    async def test_auth_check_skip_auth_case_superset_scope(self):
        """
        Test `PocketAuth.check` in the case where the auth request scope is a subset of the existing session scope.
        The auth state should be SKIP_AUTH.
        """
        # given
        future_uid = str(uuid.uuid4())
        handler = self.pocket_auth.find_handler_instance(
            name=self.auth_handler_name, auth_provider=self.auth_provider
        )
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )
        updated_auth_req = self.pocket_auth.make_request(
            auth_scopes=["scope-1"],
            auth_provider=self.auth_provider,
        )

        # when
        # set pending session
        self.pocket_auth._upsert_pending_session(
            auth_handler=handler,
            future_uid=future_uid,
            profile=self.profile,
            thread_id=self.thread_id,
            scope=set(self.scope),
        )

        # activate session
        await self.pocket_auth._set_session_active(
            context=SlackOAuth2AuthContext(
                access_token="access-token",
                refresh_token="refresh-token",
                description="test-description",
                expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=30),
            ),
            provider=self.auth_provider,
            profile=self.profile,
            thread_id=self.thread_id,
        )

        auth_state = await self.pocket_auth.check(
            auth_req=auth_req,
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )
        updated_auth_state = await self.pocket_auth.check(
            auth_req=updated_auth_req,
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(auth_state, AuthState.SKIP_AUTH)
        self.assertEqual(updated_auth_state, AuthState.SKIP_AUTH)

    async def test_auth_check_skip_auth_case_non_scoped_handler(self):
        """
        Test `PocketAuth.check` in the case where the session's handler is non-scoped.
        The auth state should be SKIP_AUTH even if the checking scope is not a subset of the existing session scope.
        """
        # given
        auth_handler_name = (
            "slack-token"  # temporarily use slack provider/handler for testing
        )
        auth_provider = AuthProvider.SLACK
        future_uid = str(uuid.uuid4())
        handler = self.pocket_auth.find_handler_instance(
            name=auth_handler_name, auth_provider=auth_provider
        )
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=auth_provider,
            auth_handler_name=auth_handler_name,
        )
        updated_auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope + ["new_scope"],
            auth_provider=auth_provider,
            auth_handler_name=auth_handler_name,
        )

        # when
        # set pending session
        self.pocket_auth._upsert_pending_session(
            auth_handler=handler,
            future_uid=future_uid,
            profile=self.profile,
            thread_id=self.thread_id,
            scope=set(self.scope),
        )

        # activate session
        await self.pocket_auth._set_session_active(
            context=SlackOAuth2AuthContext(
                access_token="access-token",
                refresh_token="refresh-token",
                description="test-description",
                expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=30),
            ),
            provider=auth_provider,
            profile=self.profile,
            thread_id=self.thread_id,
        )

        auth_state = await self.pocket_auth.check(
            auth_req=auth_req,
            auth_provider=auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )
        updated_auth_state = await self.pocket_auth.check(
            auth_req=updated_auth_req,
            auth_provider=auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(auth_state, AuthState.SKIP_AUTH)
        self.assertEqual(updated_auth_state, AuthState.SKIP_AUTH)

    async def test_auth_check_by_other_provider(self):
        """
        Test `PocketAuth.check` in the case of checking session by another provider.
        The auth state should be NO_SESSION.
        """
        # given
        future_uid = str(uuid.uuid4())
        handler = self.pocket_auth.find_handler_instance(
            name=self.auth_handler_name, auth_provider=self.auth_provider
        )
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        # when
        # set pending session
        self.pocket_auth._upsert_pending_session(
            auth_handler=handler,
            future_uid=future_uid,
            profile=self.profile,
            thread_id=self.thread_id,
            scope=set(self.scope),
        )

        # activate session
        await self.pocket_auth._set_session_active(
            context=SlackOAuth2AuthContext(
                access_token="access-token",
                refresh_token="refresh-token",
                description="test-description",
                expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=30),
            ),
            provider=self.auth_provider,
            profile=self.profile,
            thread_id=self.thread_id,
        )

        # check by other auth provider(SLACK)
        auth_state = await self.pocket_auth.check(
            auth_req=auth_req,
            auth_provider=AuthProvider.SLACK,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(auth_state, AuthState.NO_SESSION)

    async def test_auth_check_do_auth_case_new_scopes(self):
        """
        Test `PocketAuth.check` in case of checking session by new scopes, and this is not a subset of existing scopes
        The auth state Should be DO_AUTH
        """
        # given
        future_uid = str(uuid.uuid4())
        handler = self.pocket_auth.find_handler_instance(
            name=self.auth_handler_name, auth_provider=self.auth_provider
        )
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )
        updated_auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope + ["new_scope"],
            auth_provider=self.auth_provider,
        )

        # when
        # set pending session
        self.pocket_auth._upsert_pending_session(
            auth_handler=handler,
            future_uid=future_uid,
            profile=self.profile,
            thread_id=self.thread_id,
            scope=set(self.scope),
        )

        # activate session
        await self.pocket_auth._set_session_active(
            context=SlackOAuth2AuthContext(
                access_token="access-token",
                refresh_token="refresh-token",
                description="test-description",
                expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=30),
            ),
            provider=self.auth_provider,
            profile=self.profile,
            thread_id=self.thread_id,
        )

        auth_state = await self.pocket_auth.check(
            auth_req=auth_req,
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )
        updated_auth_state = await self.pocket_auth.check(
            auth_req=updated_auth_req,
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(auth_state, AuthState.SKIP_AUTH)
        self.assertEqual(updated_auth_state, AuthState.DO_AUTH)

    async def test_auth_check_do_refresh(self):
        """
        Test if checking near expired session
        The auth state Should be DO_REFRESH
        """
        # given
        future_uid = str(uuid.uuid4())
        handler = self.pocket_auth.find_handler_instance(
            name=self.auth_handler_name, auth_provider=self.auth_provider
        )
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        # when
        # set pending session
        self.pocket_auth._upsert_pending_session(
            auth_handler=handler,
            future_uid=future_uid,
            profile=self.profile,
            thread_id=self.thread_id,
            scope=set(self.scope),
        )

        # activate session
        await self.pocket_auth._set_session_active(
            context=SlackOAuth2AuthContext(
                access_token="access-token",
                refresh_token="refresh-token",
                description="test-description",
                expires_at=datetime.now(tz=timezone.utc)
                + timedelta(minutes=5),  # near expiration
            ),
            provider=self.auth_provider,
            profile=self.profile,
            thread_id=self.thread_id,
        )

        auth_state = await self.pocket_auth.check(
            auth_req=auth_req,
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertEqual(auth_state, AuthState.DO_REFRESH)

    ###################################################################################################################
    # Integration Test
    ###################################################################################################################
    async def test_prepare_no_session_case(self):
        """
        Test in case that there is no session available
        The prepare method should create new session and return prepared url
        """
        # given
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        # when
        prepared_url = await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )

        session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertIsNotNone(prepared_url)
        self.assertIsNotNone(session)
        self.assertIsNotNone(session.auth_resolve_uid)  # it's currently a pending session

    async def test_prepare_do_auth_new_scopes_case(self):
        """
        Test in case that previous session is already active but new request needs new scopes.
        It creates another new session, so the future uid is also different.
        But if the previous session state is PENDING_RESOLVE, it doesn't create new session. so the future uid is same as before.
        """
        # given
        new_scopes = self.scope + ["new-scope"]
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        new_scope_auth_req = self.pocket_auth.make_request(
            auth_scopes=new_scopes,
            auth_provider=self.auth_provider,
        )

        # when
        prepared_url = await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )

        session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # make session active
        future_data = FutureStore.get_future(session.auth_resolve_uid)
        future_data.future.set_result("test-code")
        await self.pocket_auth._set_session_active(
            context=GoogleOAuth2AuthContext(
                access_token="access-token",
                refresh_token="refresh-token",
                expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=30),
                description="test-description",
            ),
            provider=self.auth_provider,
            profile=self.profile,
            thread_id=self.thread_id,
        )

        new_scope_prepared_url = await self.pocket_auth.prepare(
            auth_req=new_scope_auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )
        new_scope_session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertNotEqual(prepared_url, new_scope_prepared_url)
        self.assertIsNotNone(new_scope_session.auth_resolve_uid)
        # future uid is different, because it makes new session
        self.assertNotEqual(
            new_scope_session.auth_resolve_uid, session.auth_resolve_uid
        )

    async def test_prepare_pending_resolve_case(self):
        """
        Test in case that the session is PENDING_RESOLVE state,
        It should return previous session's preparing url
        """
        # given
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        # when
        first_prepared_url = await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )
        first_session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )
        first_future_uid = first_session.auth_resolve_uid

        second_prepared_url = await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )
        second_session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )
        second_future_uid = second_session.auth_resolve_uid

        # then
        self.assertIsNotNone(first_prepared_url)
        self.assertIsNotNone(second_prepared_url)
        self.assertEqual(first_prepared_url, second_prepared_url)

        self.assertIsNotNone(first_session)
        self.assertIsNotNone(second_session)

        self.assertEqual(first_future_uid, second_future_uid)

    async def test_prepare_pending_resolve_new_scopes_case(self):
        """
        Test in case that the session is PENDING_RESOLVE state, but this session needs new scopes
        It should return new authentication uri including new scopes.
        But it will return same future uid as before.
        """
        # given
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        new_scope = self.scope + ["new-scope"]
        new_scope_auth_req = self.pocket_auth.make_request(
            auth_scopes=new_scope,
            auth_provider=self.auth_provider,
        )

        # when
        prepared_url = await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )
        session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )
        future_uid = session.auth_resolve_uid

        new_scope_prepared_url = await self.pocket_auth.prepare(
            auth_req=new_scope_auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )
        new_scope_session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )
        new_scope_future_uid = new_scope_session.auth_resolve_uid

        # then
        self.assertIsNotNone(prepared_url)
        self.assertIsNotNone(new_scope_prepared_url)
        self.assertNotEqual(
            prepared_url, new_scope_prepared_url
        )  # it should be different because url includes auth scopes information

        self.assertIsNotNone(session)
        self.assertIsNotNone(new_scope_session)

        self.assertEqual(future_uid, new_scope_future_uid)  # it will be same
        self.assertEqual(new_scope_session.auth_scopes, set(new_scope))

    async def test_prepare_resolved_case(self):
        """
        Test in case that the session is in a RESOLVED state.
        `prepare` method don't handle this case. so it just return None.
        """
        # given
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        # when
        # create session
        prepared_url = await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )
        session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # set session resolved
        future_data = FutureStore.get_future(session.auth_resolve_uid)
        future_data.future.set_result("test-code")

        # prepare while in resolved
        resolved_prepared_url = await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )

        # then
        self.assertIsNotNone(prepared_url)
        self.assertIsNone(
            resolved_prepared_url
        )  # should be none if auth state is RESOLVED

    async def test_prepare_skip_auth_case(self):
        """
        Test in case that the session is SKIP_AUTH state.
        `prepare` method don't handle this case. so it just return None.
        """
        # given
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        # when
        # create session
        prepared_url = await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )
        session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # make session active
        future_data = FutureStore.get_future(session.auth_resolve_uid)
        await self.pocket_auth._set_session_active(
            context=GoogleOAuth2AuthContext(
                access_token="access-token",
                refresh_token="refresh-token",
                description="test-description",
                expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=60),
            ),
            provider=self.auth_provider,
            profile=self.profile,
            thread_id=self.thread_id,
        )
        future_data.future.set_result("test-code")

        # prepare while in skip_auth
        skip_auth_prepared_url = await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )

        # then
        self.assertIsNotNone(prepared_url)
        self.assertIsNone(
            skip_auth_prepared_url
        )  # should be none if auth state is RESOLVED

    async def test_prepare_do_refresh_case(self):
        """
        Test in case that the session is DO_REFRESH state.
        `prepare` method don't handle this case. so it just return None.
        """
        # given
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        # when
        # create session
        prepared_url = await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )
        session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # make session active
        future_data = FutureStore.get_future(session.auth_resolve_uid)
        await self.pocket_auth._set_session_active(
            context=SlackOAuth2AuthContext(
                access_token="access-token",
                refresh_token="refresh-token",
                description="test-description",
                expires_at=datetime.now(tz=timezone.utc)
                + timedelta(minutes=5),  # near expiration
            ),
            provider=self.auth_provider,
            profile=self.profile,
            thread_id=self.thread_id,
        )
        future_data.future.set_result("test-code")

        # prepare while in do_refresh
        do_refresh_prepared_url = await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
        )

        # then
        self.assertIsNotNone(prepared_url)
        self.assertIsNone(
            do_refresh_prepared_url
        )  # should be none if auth state is RESOLVED

    async def test_delete_session(self):
        # given
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
        )

        # when
        await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )
        session_before_delete = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        deleted = self.pocket_auth.delete_session(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        session_after_delete = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )

        # then
        self.assertIsNotNone(session_before_delete)
        self.assertTrue(deleted)
        self.assertIsNone(session_after_delete)

    async def test_authenticate_resolved_case(self):
        """
        Test in case that preparing is complete.
        once preparing is complete, the auth state is set to `RESOLVED`
        while authenticating process, it will get authentication code from future created in prepare step
        """
        # given
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )

        mock_response = httpx.Response(
            status_code=200,
            json={
                "access_token": "access-token",
                "expires_in": 3600,
                "refresh_token": "refresh-token",
                "scope": ",".join(self.scope),
                "token_type": "Bearer",
            },
        )

        # when
        prepared_url = await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )
        session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )
        future_data = FutureStore.get_future(session.auth_resolve_uid)
        future_data.future.set_result("test-code")

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            context: GoogleOAuth2AuthContext = (
                await self.pocket_auth.authenticate_async(
                    auth_req=auth_req,
                    auth_provider=self.auth_provider,
                    thread_id=self.thread_id,
                    profile=self.profile,
                )
            )

            # then
        self.assertIsNotNone(prepared_url)
        self.assertIsNotNone(context)
        self.assertEqual(context.access_token, "access-token")
        self.assertEqual(context.refresh_token, "refresh-token")

    async def test_authenticate_skip_auth_case(self):
        """
        Test in case that the session already exists,
        It should return already existing session.
        """
        # given
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )

        mock_response = httpx.Response(
            status_code=200,
            json={
                "access_token": "access-token",
                "expires_in": 3600,
                "refresh_token": "refresh-token",
                "scope": ",".join(self.scope),
                "token_type": "Bearer",
            },
        )

        # when
        await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )
        session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )
        future_data = FutureStore.get_future(session.auth_resolve_uid)
        future_data.future.set_result("test-code")

        with patch("httpx.AsyncClient.post", return_value=mock_response):
            first_context: GoogleOAuth2AuthContext = (
                await self.pocket_auth.authenticate_async(
                    auth_req=auth_req,
                    auth_provider=self.auth_provider,
                    thread_id=self.thread_id,
                    profile=self.profile,
                )
            )

        # don't have to mocking response, because it just returns already existing session's context
        second_context: GoogleOAuth2AuthContext = (
            await self.pocket_auth.authenticate_async(
                auth_req=auth_req,
                auth_provider=self.auth_provider,
                thread_id=self.thread_id,
                profile=self.profile,
            )
        )

        # then
        self.assertEqual(first_context.access_token, second_context.access_token)
        self.assertEqual(first_context.refresh_token, second_context.refresh_token)

    async def test_authenticate_do_refresh_case(self):
        """
        Test in case of refreshing authentication.
        The outdated session should be replaced by refreshed session.
        """

        # given
        auth_req = self.pocket_auth.make_request(
            auth_scopes=self.scope,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )

        mock_response = httpx.Response(
            status_code=200,
            json={
                "access_token": "access-token",
                "expires_in": 300,
                "refresh_token": "refresh-token",
                "scope": ",".join(self.scope),
                "token_type": "Bearer",
            },
        )

        mock_refresh_response = httpx.Response(
            status_code=200,
            json={
                "access_token": "new-access-token",
                "expires_in": 3600,
                "scope": ",".join(self.scope),
                "token_type": "Bearer",
            },
        )

        # when
        await self.pocket_auth.prepare(
            auth_req=auth_req,
            profile=self.profile,
            thread_id=self.thread_id,
            auth_provider=self.auth_provider,
            auth_handler_name=self.auth_handler_name,
        )
        session = self.pocket_auth.session_storage.get(
            auth_provider=self.auth_provider,
            thread_id=self.thread_id,
            profile=self.profile,
        )
        future_data = FutureStore.get_future(session.auth_resolve_uid)
        future_data.future.set_result("test-code")

        # authenticate session at the first
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            first_context: GoogleOAuth2AuthContext = (
                await self.pocket_auth.authenticate_async(
                    auth_req=auth_req,
                    auth_provider=self.auth_provider,
                    thread_id=self.thread_id,
                    profile=self.profile,
                )
            )

        # refresh authentication
        with patch("httpx.AsyncClient.post", return_value=mock_refresh_response):
            second_context: GoogleOAuth2AuthContext = (
                await self.pocket_auth.authenticate_async(
                    auth_req=auth_req,
                    auth_provider=self.auth_provider,
                    thread_id=self.thread_id,
                    profile=self.profile,
                )
            )

        first_context_time_diff = (
            first_context.expires_at - datetime.now(tz=timezone.utc)
        ).total_seconds()
        second_context_time_diff = (
            second_context.expires_at - datetime.now(tz=timezone.utc)
        ).total_seconds()

        # then
        self.assertEqual(first_context.access_token, "access-token")
        self.assertEqual(second_context.access_token, "new-access-token")
        self.assertTrue(first_context_time_diff < 300)
        self.assertTrue(second_context_time_diff > 3000)
