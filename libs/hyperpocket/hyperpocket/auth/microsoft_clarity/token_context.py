from hyperpocket.auth.microsoft_clarity.context import MicrosoftClarityAuthContext
from hyperpocket.auth.microsoft_clarity.token_schema import (
    MicrosoftClarityTokenResponse,
)


class MicrosoftClarityTokenAuthContext(MicrosoftClarityAuthContext):
    @classmethod
    def from_microsoft_clarity_token_response(
        cls, response: MicrosoftClarityTokenResponse
    ):
        description = f"MicrosoftClarity Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
