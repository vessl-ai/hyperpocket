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
    LEVER_SANDBOX = "lever_sandbox"
    ALTOVIZ = "altoviz"
    RAVENSEOTOOLS = "ravenseotools"
    BREX = "brex"
    BITWARDEN = "bitwarden"
    DATADOG = "datadog"
    ONCEHUB = "oncehub"
    LEVER = "lever"
    NGROK = "ngrok"
    PANDADOC = "pandadoc"
    TIMEKIT = "timekit"
    FINAGE = "finage"
    DAILYBOT = "dailybot"
    WORKIOM = "workiom"
    ALCHEMY = "alchemy"
    CLOUDFLARE = "cloudflare"
    ADOBE = "adobe"
    TAVILY = "tavily"
    EXA = "exa"
    AIRTABLE = "airtable"
    BITBUCKET = "bitbucket"
    MAILCHIMP = "mailchimp"
    ASANA = "asana"
    ZOOM = "zoom"
    SALESFORCE = "salesforce"
    SPOTIFY = "spotify"
    FACEBOOK = "facebook"
    ACTIVELOOP = "activeloop"
    AGENTQL = "agentql"
    HAPPYROBOT = "happyrobot"
    LINKEDIN = "linkedin"
    WANDB = "wandb"
    APITOKEN = "apitoken"
    ZINC = "zinc"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    WEAVIATE = "weaviate"
    VALYU = "valyu"
    KRAKEN = "kraken"
    BASICAUTH = "basicauth"

    @classmethod
    def get_auth_provider(cls, auth_provider_name: str) -> "AuthProvider":
        try:
            return AuthProvider[auth_provider_name.upper()]
        except KeyError:
            raise ValueError(f"Invalid auth provider name. {auth_provider_name}")
