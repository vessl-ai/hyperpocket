# Supported Authentication Methods

This document provides an overview of the authentication methods supported by Hyperpocket.

## Supported Authentication Methods

Below is a checklist table indicating the supported authentication methods and whether they support token-based or
OAuth2-based authentication.

| Auth Provider                                                                     | Token-Based | OAuth2-Based | Expected Variable Name for Token |
|-----------------------------------------------------------------------------------|-------------|--------------|-----------------|
| [Activeloop](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/activeloop)                         | ✅          | ❌           | `ACTIVELOOP_TOKEN` |
| [Adobe](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/adobe)                         | ✅          | ❌           | `ADOBE_TOKEN` |
| [Affinity](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/affinity)                         | ✅          | ❌           | `AFFINITY_TOKEN` |
| [AgentQL](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/agentql)                         | ✅          | ❌           | `AGENTQL_TOKEN` |
| [Ahrefs](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/ahrefs)                         | ✅          | ❌           | `AHREFS_TOKEN` |
| [Airtable](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/airtable)                         | ✅          | ❌           | `AIRTABLE_TOKEN` |
| [Alchemy](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/alchemy)                         | ✅          | ❌           | `ALCHEMY_TOKEN` |
| [Altoviz](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/altoviz)                         | ✅          | ❌           | `ALTOVIZ_TOKEN` |
| [API Token(Generic)](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/apitoken)                         | ✅          | ❌           | `API_TOKEN` |
| [Asana](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/asana)                         | ❌          | ✅           | `ASANA_TOKEN` |
| [BambooHR](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/bamboohr)                         | ✅          | ❌           | `BAMBOOHR_TOKEN` |
| [Bitbucket](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/bitbucket)                 | ❌          | ✅           | `BITBUCKET_TOKEN` |
| [BitWarden](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/bitwarden)                 | ✅          | ❌           | `BITWARDEN_TOKEN` |
| [Brevo](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/brevo)                 | ✅          | ❌           | `BREVO_TOKEN` |
| [Brex](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/brex)                 | ✅          | ❌           | `BREX_TOKEN` |
| [Cal](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/cal)                   | ✅          | ❌           | `CAL_TOKEN` |
| [Calendly](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/calendly)                   | ❌          | ✅           | `CALENDLY_TOKEN` |
| [Canvas](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/canvas)                   | ✅          | ❌           | `CANVAS_TOKEN` |
| [Clickup](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/clickup)                   | ✅          | ❌           | `CLICKUP_TOKEN` |
| [Cloudflare](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/cloudflare)                   | ✅          | ❌           | `CLOUDFLARE_TOKEN` |
| [Dailybot](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/dailybot)                   | ✅          | ❌           | `DAILYBOT_TOKEN` |
| [Datadog](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/datadog)                   | ✅          | ❌           | `DATADOG_TOKEN` |
| [Discord](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/discord)                     | ✅          | ✅           | `DISCORD_TOKEN` |
| [Discord(Bot)](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/discordbot)                     | ✅          | ❌           | `DISCORDBOT_TOKEN` |
| [ElevenLabs](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/elevenlabs)                     | ✅          | ❌           | `ELEVENLABS_TOKEN` |
| [Exa](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/exa)                     | ✅          | ❌           | `EXA_TOKEN` |
| [Facebook](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/facebook)                   | ❌          | ✅           | `FACEBOOK_TOKEN` |
| [Finage](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/finage)                     | ✅          | ❌           | `FINAGE_TOKEN` |
| [GitHub](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/github)                       | ✅          | ✅           | `GITHUB_TOKEN` |
| [Google](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/google)                       | ❌          | ✅           | `GOOGLE_TOKEN` |
| [Gumloop](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/gumloop)                     | ✅          | ❌           | `GUMLOOP_TOKEN` |
| [Happyrobot](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/happyrobot)                     | ✅          | ❌           | `HAPPYROBOT_TOKEN` |
| [Heygen](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/heygen)                     | ✅          | ❌           | `HEYGEN_TOKEN` |
| [Hubspot](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/hubspot)                     | ✅          | ✅           | `HUBSPOT_TOKEN` |
| [Jira](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/jira)                           | ✅          | ✅           | `JIRA_TOKEN` |
| [Klaviyo](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/klaviyo)                     | ✅          | ❌           | `KLAVIYO_TOKEN` |
| [Lever](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/lever)                     | ✅          | ❌           | `LEVER_TOKEN` |
| [Lever(Sandbox)](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/lever_sandbox)                     | ✅          | ❌           | `LEVER_SANDBOX_TOKEN` |
| [Linear](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/linear)                       | ✅          | ✅           | `LINEAR_TOKEN` |
| [Linkedin](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/linkedin)                   | ❌          | ✅           | `LINKEDIN_TOKEN` |
| [ListenNotes](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/listennotes)                     | ✅          | ❌           | `LISTENNOTES_TOKEN` |
| [Mailchimp](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/mailchimp)                 | ❌          | ✅           | `MAILCHIMP_TOKEN` |
| [Mem0](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/mem0)                     | ✅          | ❌           | `MEM0_TOKEN` |
| [Microsoft Clarity](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/microsoft_clarity)                     | ✅          | ❌           | `MICROSOFT_CLARITY_TOKEN` |
| [Neon](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/neon)                     | ✅          | ❌           | `NEON_TOKEN` |
| [Ngrok](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/ngrok)                     | ✅          | ❌           | `NGROK_TOKEN` |
| [Notion](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/notion)                       | ✅          | ✅           | `NOTION_TOKEN` |
| [OnceHub](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/oncehub)                     | ✅          | ❌           | `ONCEHUB_TOKEN` |
| [PagerDuty](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/pagerduty)                     | ✅          | ❌           | `PAGERDUTY_TOKEN` |
| [PandaDoc](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/pandadoc)                     | ✅          | ❌           | `PANDADOC_TOKEN` |
| [Pipedrive](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/pipedrive)                     | ✅          | ❌           | `PIPEDRIVE_TOKEN` |
| [Posthog](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/posthog)                     | ✅          | ❌           | `POSTHOG_TOKEN` |
| [Raven Tools](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/ravenseotools)                     | ✅          | ❌           | `RAVENSEOTOOLS_TOKEN` |
| [Reddit](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/reddit)                       | ❌          | ✅           | `REDDIT_BOT_TOKEN` |
| [Salesforce](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/salesforce)               | ❌          | ✅           | `SALESFORCE_TOKEN` |
| [Semantic Scholar](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/semantic_scholar)               | ✅          | ❌           | `SEMANTIC_SCHOLAR_TOKEN` |
| [Sendgrid](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/sendgrid)               | ✅          | ❌           | `SENDGRID_TOKEN` |
| [SerpApi](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/serpapi)               | ✅          | ❌           | `SERPAPI_TOKEN` |
| [Slack](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/slack)                         | ✅          | ✅           | `SLACK_BOT_TOKEN` |
| [Spotify](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/spotify)                     | ❌          | ✅           | `SPOTIFY_TOKEN` |
| [Stripe](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/stripe)               | ✅          | ❌           | `STRIPE_TOKEN` |
| [Supabase](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/supabase)               | ✅          | ❌           | `SUPABASE_TOKEN` |
| [Tavily](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/tavily)               | ✅          | ❌           | `TAVILY_TOKEN` |
| [Timekit](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/timekit)               | ✅          | ❌           | `TIMEKIT_TOKEN` |
| [Trello](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/trello)               | ✅          | ❌           | `TRELLO_TOKEN` |
| [Weights and Biases](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/wandb)               | ✅          | ❌           | `WANDB_TOKEN` |
| [Weaviate](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/weaviate)               | ✅          | ❌           | `WEAVIATE_TOKEN` |
| [Workiom](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/workiom)               | ✅          | ❌           | `WORKIOM_TOKEN` |
| [X(formerly twitter)](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/x)                                 | ❌          | ✅           | `X_AUTH_TOKEN` |
| [Zinc](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/zinc)                           | ✅          | ❌           | `ZINC_TOKEN` |
| [Zoom](https://github.com/vessl-ai/hyperpocket/tree/main/libs/hyperpocket/hyperpocket/auth/zoom)                           | ❌          | ✅           | `ZOOM_TOKEN` |
