from typing import Optional

from pydantic import BaseModel, Field


class BaseAuthConfig(BaseModel):
    use_recommended_scope: bool = Field(default=True)

class OAuth2AuthConfig(BaseAuthConfig):
    client_id: str
    client_secret: str


class SlackAuthConfig(OAuth2AuthConfig):
    pass


class GoogleAuthConfig(OAuth2AuthConfig):
    pass


class GithubAuthConfig(OAuth2AuthConfig):
    pass


class CalendlyAuthConfig(OAuth2AuthConfig):
    pass


class XAuthConfig(OAuth2AuthConfig):
    pass

class JiraAuthConfig(OAuth2AuthConfig):
    pass

class HubspotAuthConfig(OAuth2AuthConfig):
    pass

class DiscordAuthConfig(OAuth2AuthConfig):
    pass

class AuthConfig(BaseModel):
    slack: Optional[SlackAuthConfig] = None
    google: Optional[GoogleAuthConfig] = None
    github: Optional[GithubAuthConfig] = None
    calendly: Optional[CalendlyAuthConfig] = None
    x: Optional[XAuthConfig] = None
    jira: Optional[JiraAuthConfig] = None
    hubspot: Optional[HubspotAuthConfig] = None
    discord: Optional[DiscordAuthConfig] = None
    use_prebuilt_auth: bool = Field(default=True)


DefaultAuthConfig = AuthConfig()
