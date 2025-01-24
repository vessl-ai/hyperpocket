import unittest

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.slack.token_context import SlackTokenAuthContext
from hyperpocket.config.session import SessionConfigRedis
from hyperpocket.session.in_memory import InMemorySessionValue
from hyperpocket.session.redis import RedisSessionStorage, RedisSessionValue


class TestRedisSessionStorage(unittest.TestCase):
    storage: RedisSessionStorage
    context: SlackTokenAuthContext

    def setUp(self):
        self.storage = RedisSessionStorage(
            SessionConfigRedis(host="localhost", port=6379, db="9")
        )
        self.storage.client.flushdb()

        self.auth_context = SlackTokenAuthContext(
            access_token="test",
            description="test-description",
            expires_at=None,
            detail=None,
        )

    def tearDown(self):
        self.storage.client.flushdb()

    def test_make_session_key(self):
        key = self.storage._make_session_key(
            auth_provider_name=AuthProvider.SLACK.name,
            thread_id="default_thread_id",
            profile="default_profile",
        )

        self.assertEqual(key, "SLACK__default_thread_id__default_profile")

    def test_make_session(self):
        session = self.storage._make_session(
            auth_provider_name=AuthProvider.SLACK.name,
            auth_scopes=["scope1", "scope2"],
            auth_context=self.auth_context,
            auth_resolve_uid="test-resolve-uid",
            is_auth_scope_universal=True,
        )

        # then
        self.assertIsInstance(session, RedisSessionValue)
        self.assertEqual(session.auth_provider_name, AuthProvider.SLACK.name)
        self.assertEqual(session.auth_context.access_token, "test")
        self.assertEqual(session.auth_context.description, "test-description")

    def test_set(self):
        session = self.storage.set(
            auth_provider=AuthProvider.SLACK,
            thread_id="default_thread_id",
            profile="default_profile",
            auth_scopes=["scope1", "scope2"],
            auth_resolve_uid="test-resolve-uid",
            auth_context=self.auth_context,
            is_auth_scope_universal=True,
        )

        self.assertIsInstance(session, InMemorySessionValue)
        self.assertEqual(session.auth_provider_name, AuthProvider.SLACK.name)
        self.assertEqual(
            session.auth_context.access_token, self.auth_context.access_token
        )
        self.assertEqual(
            session.auth_context.description, self.auth_context.description
        )

    def test_get_existing_data(self):
        # given
        self.storage.set(
            auth_provider=AuthProvider.SLACK,
            thread_id="default_thread_id",
            profile="default_profile",
            auth_scopes=["scope1", "scope2"],
            auth_resolve_uid="test-resolve-uid",
            auth_context=self.auth_context,
            is_auth_scope_universal=True,
        )

        # when
        session = self.storage.get(
            auth_provider=AuthProvider.SLACK,
            thread_id="default_thread_id",
            profile="default_profile",
        )

        # then
        self.assertIsInstance(session, InMemorySessionValue)
        self.assertEqual(session.auth_provider_name, AuthProvider.SLACK.name)
        self.assertEqual(session.auth_context.access_token, "test")
        self.assertEqual(session.auth_context.description, "test-description")

    def test_get_not_existing_data(self):
        # when
        session = self.storage.get(
            auth_provider=AuthProvider.SLACK,
            thread_id="default_thread_id",
            profile="default_profile",
        )

        # then
        self.assertIsNone(session)

    def test_delete_existing_data(self):
        # given
        self.storage.set(
            auth_provider=AuthProvider.SLACK,
            thread_id="default_thread_id",
            profile="default_profile",
            auth_scopes=["scope1", "scope2"],
            auth_resolve_uid="test-resolve-uid",
            auth_context=self.auth_context,
            is_auth_scope_universal=True,
        )

        # when
        before_session = self.storage.get(
            auth_provider=AuthProvider.SLACK,
            thread_id="default_thread_id",
            profile="default_profile",
        )

        deleted = self.storage.delete(
            auth_provider=AuthProvider.SLACK,
            thread_id="default_thread_id",
            profile="default_profile",
        )

        after_session = self.storage.get(
            auth_provider=AuthProvider.SLACK,
            thread_id="default_thread_id",
            profile="default_profile",
        )

        # then
        self.assertTrue(deleted)
        self.assertIsNotNone(before_session)
        self.assertIsNone(after_session)

    def test_delete_not_existing_data(self):
        deleted = self.storage.delete(
            auth_provider=AuthProvider.SLACK,
            thread_id="default_thread_id",
            profile="default_profile",
        )

        # then
        self.assertFalse(deleted)
