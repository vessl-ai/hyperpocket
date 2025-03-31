from hyperpocket.auth.basicauth.context import BasicAuthContext
from hyperpocket.auth.basicauth.basicauth_schema import (
    BasicAuthResponse,
)


class BasicAuthContext(BasicAuthContext):
    @classmethod
    def from_api_token_response(cls, response: BasicAuthResponse):
        description = "Api Token Context logged in"

        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
