from hyperpocket.auth.timekit.context import TimekitAuthContext
from hyperpocket.auth.timekit.token_schema import TimekitTokenResponse


class TimekitTokenAuthContext(TimekitAuthContext):
    @classmethod
    def from_timekit_token_response(cls, response: TimekitTokenResponse):
        description = f"Timekit Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
