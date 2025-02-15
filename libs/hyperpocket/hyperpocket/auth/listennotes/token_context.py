from hyperpocket.auth.listennotes.context import ListennotesAuthContext
from hyperpocket.auth.listennotes.token_schema import ListennotesTokenResponse


class ListennotesTokenAuthContext(ListennotesAuthContext):
    @classmethod
    def from_listennotes_token_response(cls, response: ListennotesTokenResponse):
        description = f"Listennotes Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
