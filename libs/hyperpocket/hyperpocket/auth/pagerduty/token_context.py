from hyperpocket.auth.pagerduty.context import PagerdutyAuthContext
from hyperpocket.auth.pagerduty.token_schema import PagerdutyTokenResponse


class PagerdutyTokenAuthContext(PagerdutyAuthContext):
    @classmethod
    def from_pagerduty_token_response(cls, response: PagerdutyTokenResponse):
        description = f"Pagerduty Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
