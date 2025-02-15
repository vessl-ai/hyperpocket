from hyperpocket.auth.sendgrid.context import SendgridAuthContext
from hyperpocket.auth.sendgrid.token_schema import SendgridTokenResponse


class SendgridTokenAuthContext(SendgridAuthContext):
    @classmethod
    def from_sendgrid_token_response(cls, response: SendgridTokenResponse):
        description = f"Sendgrid Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
