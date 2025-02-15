from hyperpocket.auth.trello.context import TrelloAuthContext
from hyperpocket.auth.trello.token_schema import TrelloTokenResponse


class TrelloTokenAuthContext(TrelloAuthContext):
    @classmethod
    def from_trello_token_response(cls, response: TrelloTokenResponse):
        description = f"Trello Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
