from hyperpocket.auth.neon.context import NeonAuthContext
from hyperpocket.auth.neon.token_schema import NeonTokenResponse


class NeonTokenAuthContext(NeonAuthContext):
    @classmethod
    def from_neon_token_response(cls, response: NeonTokenResponse):
        description = f"Neon Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
