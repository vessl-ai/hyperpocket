from typing import Optional
from urllib.parse import urlencode, urljoin

from hyperpocket.auth import AuthHandlerInterface, AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.github.token_context import GitHubTokenAuthContext
from hyperpocket.auth.github.token_schema import GitHubTokenRequest, GitHubTokenResponse
from hyperpocket.auth.schema import AuthenticateRequest
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class GitHubTokenAuthHandler(AuthHandlerInterface):
    name: str = "github-token"
    description: str = (
        "This handler is used to authenticate users using the GitHub token."
    )
    scoped: bool = False

    _TOKEN_URL: str = urljoin(
        config().public_base_url + "/",
        f"{config().callback_url_rewrite_prefix}/auth/token",
    )

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.GITHUB

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: AuthenticateRequest,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/github/token/callback",
        )
        auth_url = self._make_auth_url(
            auth_req=auth_req, redirect_uri=redirect_uri, state=future_uid
        )
        FutureStore.create_future(
            future_uid,
            data={
                "redirect_uri": redirect_uri,
                "thread_id": thread_id,
                "profile": profile,
            },
        )

        return f"User needs to authenticate using the following URL: {auth_url}"

    async def authenticate(
        self, auth_req: GitHubTokenRequest, future_uid: str, *args, **kwargs
    ) -> GitHubTokenAuthContext:
        future_data = FutureStore.get_future(future_uid)
        access_token = await future_data.future

        response = GitHubTokenResponse(access_token=access_token)
        context = GitHubTokenAuthContext.from_github_token_response(response)

        return context

    async def refresh(
        self, auth_req: GitHubTokenRequest, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        raise Exception("GitHub token doesn't support refresh")

    def _make_auth_url(
        self, auth_req: GitHubTokenRequest, redirect_uri: str, state: str
    ):
        params = {"redirect_uri": redirect_uri, "state": state}
        return f"{self._TOKEN_URL}?{urlencode(params)}"

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> GitHubTokenRequest:
        return GitHubTokenRequest()
