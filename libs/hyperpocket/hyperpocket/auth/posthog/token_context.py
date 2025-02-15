from hyperpocket.auth.posthog.context import PosthogAuthContext
from hyperpocket.auth.posthog.token_schema import PosthogTokenResponse


class PosthogTokenAuthContext(PosthogAuthContext):
    @classmethod
    def from_posthog_token_response(cls, response: PosthogTokenResponse):
        description = f"Posthog Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
