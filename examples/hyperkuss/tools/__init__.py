from typing import List, Callable
from hyperpocket.tool import function_tool
from . import hubspot_tools
from . import twilio_tools
from . import system_tools
from . import notion_tools
from . import slack_tools
from . import google_tools

# List of all available tools
AVAILABLE_TOOLS: List[Callable] = [
    # System tools
    system_tools.list_tools,
    # HubSpot tools
    hubspot_tools.search_contacts,
    hubspot_tools.create_contact,
    hubspot_tools.get_contact_by_id,
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
    }
} 