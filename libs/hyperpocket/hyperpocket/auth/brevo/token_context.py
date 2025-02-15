from hyperpocket.auth.brevo.context import BrevoAuthContext
from hyperpocket.auth.brevo.token_schema import BrevoTokenResponse


class BrevoTokenAuthContext(BrevoAuthContext):
    @classmethod
    def from_brevo_token_response(cls, response: BrevoTokenResponse):
        description = f"Brevo Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
