from enum import Enum


class AuthProvider(Enum):
    SLACK = "slack"
    LINEAR = "linear"
    GITHUB = "github"
    GOOGLE = "google"
    CALENDLY = "calendly"
    NOTION = "notion"
    REDDIT = "reddit"
    GUMLOOP = "gumloop"
    SERPAPI = "serpapi"
    X = "x"
    APITOKEN = "apitoken"

    @classmethod
    def get_auth_provider(cls, auth_provider_name: str) -> "AuthProvider":
        try:
            return AuthProvider[auth_provider_name.upper()]
        except KeyError:
            raise ValueError(f"Invalid auth provider name. {auth_provider_name}")
