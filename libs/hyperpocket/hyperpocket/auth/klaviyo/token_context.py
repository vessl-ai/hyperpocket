from hyperpocket.auth.klaviyo.context import KlaviyoAuthContext
from hyperpocket.auth.klaviyo.token_schema import KlaviyoTokenResponse


class KlaviyoTokenAuthContext(KlaviyoAuthContext):
    @classmethod
    def from_klaviyo_token_response(cls, response: KlaviyoTokenResponse):
        description = f"Klaviyo Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
