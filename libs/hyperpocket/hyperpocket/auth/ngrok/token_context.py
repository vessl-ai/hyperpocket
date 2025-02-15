from hyperpocket.auth.ngrok.context import NgrokAuthContext
from hyperpocket.auth.ngrok.token_schema import NgrokTokenResponse


class NgrokTokenAuthContext(NgrokAuthContext):
    @classmethod
    def from_ngrok_token_response(cls, response: NgrokTokenResponse):
        description = f"Ngrok Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
