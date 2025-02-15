from hyperpocket.auth.mem0.context import Mem0AuthContext
from hyperpocket.auth.mem0.token_schema import Mem0TokenResponse


class Mem0TokenAuthContext(Mem0AuthContext):
    @classmethod
    def from_mem0_token_response(cls, response: Mem0TokenResponse):
        description = f"Mem0 Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
