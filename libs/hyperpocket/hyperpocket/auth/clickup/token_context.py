from hyperpocket.auth.clickup.context import ClickupAuthContext
from hyperpocket.auth.clickup.token_schema import ClickupTokenResponse


class ClickupTokenAuthContext(ClickupAuthContext):
    @classmethod
    def from_clickup_token_response(cls, response: ClickupTokenResponse):
        description = f"Clickup Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
