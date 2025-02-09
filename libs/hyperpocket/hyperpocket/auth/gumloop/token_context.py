from hyperpocket.auth.gumloop.context import GumLoopContext
from hyperpocket.auth.gumloop.token_schema import GumloopTokenResponse


class GumLoopTokenContext(GumLoopContext):
    @classmethod
    def from_gumloop_token_response(cls, response: GumloopTokenResponse):
        description = "Gumloop Token Context logged in"

        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
