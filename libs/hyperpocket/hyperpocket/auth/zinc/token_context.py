from hyperpocket.auth.zinc.context import ZincAuthContext
from hyperpocket.auth.zinc.token_schema import ZincTokenResponse
class ZincTokenAuthContext(ZincAuthContext):
    @classmethod
    def from_zinc_token_response(cls, response: ZincTokenResponse):
        description = f'Zinc Token Context logged in'
        return cls(
            access_token=response.access_token,
            description=description,
            expires_at=None
        )