from hyperpocket.auth.valyu.context import ValyuAuthContext
from hyperpocket.auth.valyu.token_schema import ValyuTokenResponse


class ValyuTokenAuthContext(ValyuAuthContext):
    @classmethod
    def from_valyu_token_response(cls, response: ValyuTokenResponse):
        description = f"Valyu Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
