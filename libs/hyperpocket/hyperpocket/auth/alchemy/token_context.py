from hyperpocket.auth.alchemy.context import AlchemyAuthContext
from hyperpocket.auth.alchemy.token_schema import AlchemyTokenResponse


class AlchemyTokenAuthContext(AlchemyAuthContext):
    @classmethod
    def from_alchemy_token_response(cls, response: AlchemyTokenResponse):
        description = f"Alchemy Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
