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


class ZoomAuthConfig(OAuth2AuthConfig):
    pass


class AsanaAuthConfig(OAuth2AuthConfig):
    pass


class MailchimpAuthConfig(OAuth2AuthConfig):
    pass


class BitbucketAuthConfig(OAuth2AuthConfig):
    pass


class NotionAuthConfig(OAuth2AuthConfig):
    pass


class LinkedinAuthConfig(OAuth2AuthConfig):
    pass


class LinearAuthConfig(OAuth2AuthConfig):
    pass


class SalesForceAuthConfig(OAuth2AuthConfig):
    domain_url: str


class SpotifyAuthConfig(OAuth2AuthConfig):
    pass


class FacebookAuthConfig(OAuth2AuthConfig):
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
    zoom: Optional[ZoomAuthConfig] = None
    asana: Optional[AsanaAuthConfig] = None
    mailchimp: Optional[MailchimpAuthConfig] = None
    bitbucket: Optional[BitbucketAuthConfig] = None
    notion: Optional[NotionAuthConfig] = None
    salesforce: Optional[SalesForceAuthConfig] = None
    spotify: Optional[SpotifyAuthConfig] = None
    linkedin: Optional[LinkedinAuthConfig] = None
    linear: Optional[LinearAuthConfig] = None
    facebook: Optional[FacebookAuthConfig] = None
    use_prebuilt_auth: bool = Field(default=True)
    auth_encryption_secret_key: Optional[str] = Field(default=None)


DefaultAuthConfig = AuthConfig()
