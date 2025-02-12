from typing import Optional

from pydantic import BaseModel, Field


class BaseAuthConfig(BaseModel):
    use_recommended_scope: bool = Field(default=True)


class SlackAuthConfig(BaseAuthConfig):
    client_id: str
    client_secret: str


class GoogleAuthConfig(BaseAuthConfig):
    client_id: str
    client_secret: str


class GithubAuthConfig(BaseAuthConfig):
    client_id: str
    client_secret: str


class CalendlyAuthConfig(BaseAuthConfig):
    client_id: str
    client_secret: str


class XAuthConfig(BaseAuthConfig):
    client_id: str
    client_secret: str


class AuthConfig(BaseModel):
    slack: Optional[SlackAuthConfig] = None
    google: Optional[GoogleAuthConfig] = None
    github: Optional[GithubAuthConfig] = None
    calendly: Optional[CalendlyAuthConfig] = None
    x: Optional[XAuthConfig] = None
    use_prebuilt_auth: bool = Field(default=True)


DefaultAuthConfig = AuthConfig()
