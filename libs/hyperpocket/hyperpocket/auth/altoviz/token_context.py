from hyperpocket.auth.altoviz.context import AltovizAuthContext
from hyperpocket.auth.altoviz.token_schema import AltovizTokenResponse


class AltovizTokenAuthContext(AltovizAuthContext):
    @classmethod
    def from_altoviz_token_response(cls, response: AltovizTokenResponse):
        description = f"Altoviz Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
