from hyperpocket.auth.serpapi.context import SerpapiAuthContext
from hyperpocket.auth.serpapi.token_schema import SerpapiTokenResponse


class SerpapiTokenAuthContext(SerpapiAuthContext):
    @classmethod
    def from_serpapi_token_response(cls, response: SerpapiTokenResponse):
        description = f"Serpapi Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
