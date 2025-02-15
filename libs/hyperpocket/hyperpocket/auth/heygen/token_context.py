from hyperpocket.auth.heygen.context import HeygenAuthContext
from hyperpocket.auth.heygen.token_schema import HeygenTokenResponse


class HeygenTokenAuthContext(HeygenAuthContext):
    @classmethod
    def from_heygen_token_response(cls, response: HeygenTokenResponse):
        description = f"Heygen Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
