from hyperpocket.auth.adobe.context import AdobeAuthContext
from hyperpocket.auth.adobe.token_schema import AdobeTokenResponse


class AdobeTokenAuthContext(AdobeAuthContext):
    @classmethod
    def from_adobe_token_response(cls, response: AdobeTokenResponse):
        description = f"Adobe Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
