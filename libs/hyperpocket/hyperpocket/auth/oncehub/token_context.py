from hyperpocket.auth.oncehub.context import OncehubAuthContext
from hyperpocket.auth.oncehub.token_schema import OncehubTokenResponse


class OncehubTokenAuthContext(OncehubAuthContext):
    @classmethod
    def from_oncehub_token_response(cls, response: OncehubTokenResponse):
        description = f"Oncehub Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
