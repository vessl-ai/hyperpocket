from hyperpocket.auth.jira.context import JiraAuthContext
from hyperpocket.auth.jira.token_schema import JiraTokenResponse


class JiraTokenAuthContext(JiraAuthContext):
    @classmethod
    def from_jira_token_response(cls, response: JiraTokenResponse):
        description = f"Jira Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
