from hyperpocket.auth.notion.context import NotionAuthContext
from hyperpocket.auth.notion.token_schema import NotionTokenResponse


class NotionTokenAuthContext(NotionAuthContext):
    @classmethod
    def from_notion_token_response(cls, response: NotionTokenResponse):
        description = "Notion Token Context logged in"

        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
