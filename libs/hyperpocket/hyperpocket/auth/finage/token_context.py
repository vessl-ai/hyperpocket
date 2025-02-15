from hyperpocket.auth.finage.context import FinageAuthContext
from hyperpocket.auth.finage.token_schema import FinageTokenResponse


class FinageTokenAuthContext(FinageAuthContext):
    @classmethod
    def from_finage_token_response(cls, response: FinageTokenResponse):
        description = f"Finage Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
