from hyperpocket.auth.linkedin.context import LinkedinAuthContext
from hyperpocket.auth.linkedin.basicauth_schema import LinkedinBasicAuthResponse


class LinkedinBasicAuthContext(LinkedinAuthContext):
    _ACCESS_TOKEN_KEY: str = "LINKEDIN_BASIC_AUTH"

    @classmethod
    def from_api_token_response(cls, response: LinkedinBasicAuthResponse):
        description = "Api Token Context logged in"

        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
