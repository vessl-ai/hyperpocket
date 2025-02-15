from hyperpocket.auth.activeloop.context import ActiveloopAuthContext
from hyperpocket.auth.activeloop.token_schema import ActiveloopTokenResponse


class ActiveloopTokenAuthContext(ActiveloopAuthContext):
    @classmethod
    def from_activeloop_token_response(cls, response: ActiveloopTokenResponse):
        description = f"Activeloop Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
