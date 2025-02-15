from hyperpocket.auth.bamboohr.context import BamboohrAuthContext
from hyperpocket.auth.bamboohr.token_schema import BamboohrTokenResponse


class BamboohrTokenAuthContext(BamboohrAuthContext):
    @classmethod
    def from_bamboohr_token_response(cls, response: BamboohrTokenResponse):
        description = f"Bamboohr Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
