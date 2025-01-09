from datetime import datetime, timedelta, timezone

from hyperpocket.auth.github.context import GitHubAuthContext
from hyperpocket.auth.github.oauth2_schema import GitHubOAuth2Response


class GitHubOAuth2AuthContext(GitHubAuthContext):
    @classmethod
    def from_github_oauth2_response(
        cls, response: GitHubOAuth2Response
    ) -> "GitHubOAuth2AuthContext":
        description = f"Github OAuth2 Context logged in with {response.scope} scopes"
        now = datetime.now(tz=timezone.utc)

        if response.expires_in:
            expires_at = now + timedelta(seconds=response.expires_in)
        else:
            expires_at = None

        return cls(
            access_token=response.access_token,
            description=description,
            expires_at=expires_at,
            detail=response,
        )
