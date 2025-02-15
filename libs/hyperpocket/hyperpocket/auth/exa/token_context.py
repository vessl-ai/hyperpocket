from hyperpocket.auth.exa.context import ExaAuthContext
from hyperpocket.auth.exa.token_schema import ExaTokenResponse


class ExaTokenAuthContext(ExaAuthContext):
    @classmethod
    def from_exa_token_response(cls, response: ExaTokenResponse):
        description = f"Exa Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
