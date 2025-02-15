from hyperpocket.auth.bitwarden.context import BitwardenAuthContext
from hyperpocket.auth.bitwarden.token_schema import BitwardenTokenResponse


class BitwardenTokenAuthContext(BitwardenAuthContext):
    @classmethod
    def from_bitwarden_token_response(cls, response: BitwardenTokenResponse):
        description = f"Bitwarden Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
