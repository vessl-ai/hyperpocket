from typing import List, Callable
from hyperpocket.tool import function_tool
from . import hubspot_tools
from . import twilio_tools
from . import system_tools
from . import notion_tools
from . import slack_tools
from . import google_tools
from . import linkedin_tools
from . import attio_tools
from . import firecrawl_tools

# List of all available tools
AVAILABLE_TOOLS: List[Callable] = [
    # System tools
    system_tools.list_tools,
    # HubSpot tools
    hubspot_tools.search_contacts,
    hubspot_tools.create_contact,
    hubspot_tools.get_contact_by_id,
    hubspot_tools.get_deal_details,
    hubspot_tools.list_deals,
    # Twilio tools
    twilio_tools.make_phone_call,
    twilio_tools.check_call_status,
    twilio_tools.verify_phone_number,
    twilio_tools.list_verified_numbers,
    twilio_tools.send_sms,
    # Notion tools
    notion_tools.search_pages,
    notion_tools.create_page,
    notion_tools.get_page_content,
    # Slack tools
    slack_tools.get_mention_messages,
    slack_tools.summarize_thread,
    slack_tools.help_with_thread,
    # Google tools
    google_tools.create_meet_link,
    google_tools.get_meetings,
    # LinkedIn tools
    linkedin_tools.get_profile_info,
    # Attio tools
    attio_tools.get_deal_info,
    attio_tools.list_workspace_objects,
    # Firecrawl tools
    firecrawl_tools.summarize_website,
]

# Tool categories metadata
TOOL_CATEGORIES = {
    "system": {
        "name": "System Tools",
        "description": "Tools for managing and listing other tools",
        "tools": [
            system_tools.list_tools
        ]
    },
    "hubspot": {
        "name": "HubSpot",
        "description": "Tools for interacting with HubSpot CRM",
        "tools": [
            hubspot_tools.search_contacts,
            hubspot_tools.create_contact,
            hubspot_tools.get_contact_by_id,
            hubspot_tools.get_deal_details,
            hubspot_tools.list_deals,
        ]
    },
    "twilio": {
        "name": "Twilio Communication",
        "description": "Tools for making calls and sending SMS messages via Twilio",
        "tools": [
            twilio_tools.make_phone_call,
            twilio_tools.check_call_status,
            twilio_tools.verify_phone_number,
            twilio_tools.list_verified_numbers,
            twilio_tools.send_sms,
        ]
    },
    "notion": {
        "name": "Notion",
        "description": "Tools for managing Notion pages and documents",
        "tools": [
            notion_tools.search_pages,
            notion_tools.create_page,
            notion_tools.get_page_content,
        ]
    },
    "slack": {
        "name": "Slack",
        "description": "Tools for interacting with Slack messages and channels",
        "tools": [
            slack_tools.get_mention_messages,
            slack_tools.summarize_thread,
            slack_tools.help_with_thread,
        ]
    },
    "google": {
        "name": "Google",
        "description": "Tools for Google services like Meet and Calendar",
        "tools": [
            google_tools.create_meet_link,
            google_tools.get_meetings,
        ]
    },
    "linkedin": {
        "name": "LinkedIn",
        "description": "Tools for accessing LinkedIn profile information",
        "tools": [
            linkedin_tools.get_profile_info,
        ]
    },
    "attio": {
        "name": "Attio",
        "description": "Tools for interacting with Attio CRM",
        "tools": [
            attio_tools.get_deal_info,
            attio_tools.list_workspace_objects,
        ]
    },
    "firecrawl": {
        "name": "Firecrawl",
        "description": "Tools for crawling and summarizing web content",
        "tools": [
            firecrawl_tools.summarize_website,
        ]
    }
} 