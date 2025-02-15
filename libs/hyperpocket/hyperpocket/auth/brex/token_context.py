from hyperpocket.auth.brex.context import BrexAuthContext
from hyperpocket.auth.brex.token_schema import BrexTokenResponse


class BrexTokenAuthContext(BrexAuthContext):
    @classmethod
    def from_brex_token_response(cls, response: BrexTokenResponse):
        description = f"Brex Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
