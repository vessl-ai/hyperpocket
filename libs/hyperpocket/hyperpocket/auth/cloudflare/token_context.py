from hyperpocket.auth.cloudflare.context import CloudflareAuthContext
from hyperpocket.auth.cloudflare.token_schema import CloudflareTokenResponse


class CloudflareTokenAuthContext(CloudflareAuthContext):
    @classmethod
    def from_cloudflare_token_response(cls, response: CloudflareTokenResponse):
        description = f"Cloudflare Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
