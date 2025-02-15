from hyperpocket.auth.ahrefs.context import AhrefsAuthContext
from hyperpocket.auth.ahrefs.token_schema import AhrefsTokenResponse


class AhrefsTokenAuthContext(AhrefsAuthContext):
    @classmethod
    def from_ahrefs_token_response(cls, response: AhrefsTokenResponse):
        description = f"Ahrefs Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
