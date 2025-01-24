from hyperpocket.auth.linear.context import LinearAuthContext
from hyperpocket.auth.linear.token_schema import LinearTokenResponse


class LinearTokenAuthContext(LinearAuthContext):
    @classmethod
    def from_linear_token_response(cls, response: LinearTokenResponse):
        description = "Linear Token Context logged in"

        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
