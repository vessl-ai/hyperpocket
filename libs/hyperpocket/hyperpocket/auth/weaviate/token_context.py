from hyperpocket.auth.weaviate.context import WeaviateAuthContext
from hyperpocket.auth.weaviate.token_schema import WeaviateTokenResponse
class WeaviateTokenAuthContext(WeaviateAuthContext):
    @classmethod
    def from_weaviate_token_response(cls, response: WeaviateTokenResponse):
        description = f'Weaviate Token Context logged in'
        return cls(
            access_token=response.access_token,
            description=description,
            expires_at=None
        )