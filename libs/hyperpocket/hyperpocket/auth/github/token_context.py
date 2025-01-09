from hyperpocket.auth.github.context import GitHubAuthContext
from hyperpocket.auth.github.token_schema import GitHubTokenResponse


class GitHubTokenAuthContext(GitHubAuthContext):
    @classmethod
    def from_github_token_response(cls, response: GitHubTokenResponse):
        description = "GitHub Token Context logged in"

        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
