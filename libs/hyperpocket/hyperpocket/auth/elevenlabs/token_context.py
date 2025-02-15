from hyperpocket.auth.elevenlabs.context import ElevenlabsAuthContext
from hyperpocket.auth.elevenlabs.token_schema import ElevenlabsTokenResponse


class ElevenlabsTokenAuthContext(ElevenlabsAuthContext):
    @classmethod
    def from_elevenlabs_token_response(cls, response: ElevenlabsTokenResponse):
        description = f"Elevenlabs Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
