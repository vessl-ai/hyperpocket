from hyperpocket.auth.slack.context import SlackAuthContext
from hyperpocket.auth.slack.token_schema import SlackTokenResponse


class SlackTokenAuthContext(SlackAuthContext):
    @classmethod
    def from_slack_token_response(cls, response: SlackTokenResponse):
        description = "Slack Token Context logged in"

        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
