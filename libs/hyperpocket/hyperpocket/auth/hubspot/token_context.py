from hyperpocket.auth.hubspot.context import HubspotAuthContext
from hyperpocket.auth.hubspot.token_schema import HubspotTokenResponse


class HubspotTokenAuthContext(HubspotAuthContext):
    @classmethod
    def from_hubspot_token_response(cls, response: HubspotTokenResponse):
        description = f"Hubspot Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
