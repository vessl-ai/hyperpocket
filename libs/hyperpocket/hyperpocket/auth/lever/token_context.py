from hyperpocket.auth.lever.context import LeverAuthContext
from hyperpocket.auth.lever.token_schema import LeverTokenResponse


class LeverTokenAuthContext(LeverAuthContext):
    @classmethod
    def from_lever_token_response(cls, response: LeverTokenResponse):
        description = f"Lever Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
