from hyperpocket.auth.affinity.context import AffinityAuthContext
from hyperpocket.auth.affinity.token_schema import AffinityTokenResponse


class AffinityTokenAuthContext(AffinityAuthContext):
    @classmethod
    def from_affinity_token_response(cls, response: AffinityTokenResponse):
        description = f"Affinity Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
