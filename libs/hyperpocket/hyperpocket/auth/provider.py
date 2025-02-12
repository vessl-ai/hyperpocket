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
    X = "x"
    JIRA = "jira"
    SENDGRID = "sendgird"
    POSTHOG = "posthog"
    PAGERDUTY = "pagerduty"
    PIPEDRIVE = "pipedrive"
    KLAVIYO = "klaviyo"
    BREVO = "brevo"
    BAMBOOHR = "bamboohr"
    CAL = "cal"
    CLICKUP = "clickup"
    SUPABASE = "supabase"
    NEON = "neon"
    CANVAS = "canvas"
    ELEVENLABS = "elevenlabs"
    AHREFS = "ahrefs"
    MEM0 = "mem0"
    HEYGEN = "heygen"
    LISTENNOTES = "listennotes"
    STRIPE = "stripe"
    AFFINITY = "affinity"
    TRELLO = "trello"
    HUBSPOT = "hubspot"
    DISCORD = "discord"
    DISCORDBOT = "discordbot"
    MICROSOFT_CLARITY = "microsoft_clarity"

    @classmethod
    def get_auth_provider(cls, auth_provider_name: str) -> "AuthProvider":
        try:
            return AuthProvider[auth_provider_name.upper()]
        except KeyError:
            raise ValueError(f"Invalid auth provider name. {auth_provider_name}")
