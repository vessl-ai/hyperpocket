from hyperpocket.auth.apitoken.context import ApiTokenAuthContext
from hyperpocket.auth.apitoken.token_schema import ApiTokenResponse


class ApiTokenAuthContext(ApiTokenAuthContext):
    @classmethod
    def from_api_token_response(cls, response: ApiTokenResponse):
        description = "Api Token Context logged in"

        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
