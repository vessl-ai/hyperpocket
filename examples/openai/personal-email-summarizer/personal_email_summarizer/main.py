import datetime
import json
import os

import openai
import requests

from hyperpocket.auth.provider import AuthProvider
from hyperpocket.tool.function.annotation import function_tool
from hyperpocket_openai import PocketOpenAI


def summarize_email(content):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Summarize this email: {content}"}],
    )
    return response["choices"][0]["message"]["content"]


def is_important_email(subject, sender, content):
    important_senders = []
    urgent_keywords = ["urgent", "deadline", "reply needed"]
    if sender in important_senders:
        return True
    if any(keyword in content.lower() for keyword in urgent_keywords):
        return True
    return False


class BuiltinTools:
    @classmethod
    def github(cls):
        return [
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/list-pull-requests",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/read-pull-request",
        ]

    @classmethod
    def google_calendar(cls):
        return [
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-events",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/get-calendar-list",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/insert-calendar-events",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/google/delete-calendar-event",
        ]

    @classmethod
    def slack(cls):
        return [
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/get-messages",
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/slack/post-message",
        ]

    @classmethod
    def linear(cls):
        return [
            "https://github.com/vessl-ai/hyperpocket/tree/main/tools/linear/get-issues"
        ]


@function_tool()
def get_gmail_query_definition(**kwargs):
    return json.dumps(
        {
            "search_operators": [
                {
                    "operator": "from:",
                    "description": "Find emails sent from a specific person.",
                    "examples": ["from:me", "from:amy@example.com"],
                },
                {
                    "operator": "to:",
                    "description": "Find emails sent to a specific person.",
                    "examples": ["to:me", "to:john@example.com"],
                },
                {
                    "operator": "cc:",
                    "description": "Find emails that include specific people in the 'Cc' field.",
                    "examples": ["cc:john@example.com"],
                },
                {
                    "operator": "bcc:",
                    "description": "Find emails that include specific people in the 'Bcc' field.",
                    "examples": ["bcc:david@example.com"],
                },
                {
                    "operator": "subject:",
                    "description": "Find emails by a word or phrase in the subject line.",
                    "examples": ["subject:dinner", "subject:anniversary party"],
                },
                {
                    "operator": "after:",
                    "description": "Search for emails received after a specific date.",
                    "examples": ["after:2004/04/16", "after:04/16/2004"],
                },
                {
                    "operator": "before:",
                    "description": "Search for emails received before a specific date.",
                    "examples": ["before:2004/04/18", "before:04/18/2004"],
                },
                {
                    "operator": "older_than:",
                    "description": "Search for emails older than a time period.",
                    "examples": ["older_than:1y"],
                },
                {
                    "operator": "newer_than:",
                    "description": "Search for emails newer than a time period.",
                    "examples": ["newer_than:2d"],
                },
                {
                    "operator": "OR or { }",
                    "description": "Find emails that match one or more of your search criteria.",
                    "examples": ["from:amy OR from:david", "{from:amy from:david}"],
                },
                {
                    "operator": "AND",
                    "description": "Find emails that match all of your search criteria.",
                    "examples": ["from:amy AND to:david"],
                },
                {
                    "operator": "-",
                    "description": "Exclude emails from your search criteria.",
                    "examples": ["dinner -movie"],
                },
                {
                    "operator": "AROUND",
                    "description": "Find emails with words near each other.",
                    "examples": [
                        "holiday AROUND 10 vacation",
                        '"secret AROUND 25 birthday"',
                    ],
                },
                {
                    "operator": "label:",
                    "description": "Find emails under one of your labels.",
                    "examples": ["label:friends", "label:important"],
                },
                {
                    "operator": "category:",
                    "description": "Find emails under one of your inbox categories.",
                    "examples": [
                        "category:primary",
                        "category:social",
                        "category:promotions",
                    ],
                },
                {
                    "operator": "has:",
                    "description": "Find emails that include specific items.",
                    "examples": [
                        "has:attachment",
                        "has:youtube",
                        "has:drive",
                        "has:document",
                    ],
                },
                {
                    "operator": "list:",
                    "description": "Find emails from a mailing list.",
                    "examples": ["list:info@example.com"],
                },
                {
                    "operator": "filename:",
                    "description": "Find emails that have attachments with a specific name or file type.",
                    "examples": ["filename:pdf", "filename:homework.txt"],
                },
                {
                    "operator": '" "',
                    "description": "Search for emails with an exact word or phrase.",
                    "examples": ['"dinner and movie tonight"'],
                },
                {
                    "operator": "( )",
                    "description": "Group multiple search terms together.",
                    "examples": ["subject:(dinner movie)"],
                },
                {
                    "operator": "in:anywhere",
                    "description": "Find emails across Gmail, including Spam and Trash.",
                    "examples": ["in:anywhere movie"],
                },
                {
                    "operator": "in:snoozed",
                    "description": "Find emails that you snoozed.",
                    "examples": ["in:snoozed birthday reminder"],
                },
                {
                    "operator": "is:muted",
                    "description": "Find emails that you muted.",
                    "examples": ["is:muted subject:team celebration"],
                },
                {
                    "operator": "is:",
                    "description": "Search for emails by their status.",
                    "examples": ["is:important", "is:starred", "is:unread", "is:read"],
                },
                {
                    "operator": "has:",
                    "description": "Search for emails with specific stars or symbols.",
                    "examples": ["has:yellow-star", "has:purple-question"],
                },
                {
                    "operator": "deliveredto:",
                    "description": "Find emails delivered to a specific email address.",
                    "examples": ["deliveredto:username@example.com"],
                },
                {
                    "operator": "size:",
                    "description": "Find emails by their size.",
                    "examples": ["size:1000000"],
                },
                {
                    "operator": "larger:",
                    "description": "Find emails larger than a certain size.",
                    "examples": ["larger:10M"],
                },
                {
                    "operator": "smaller:",
                    "description": "Find emails smaller than a certain size.",
                    "examples": ["smaller:5M"],
                },
                {
                    "operator": "+",
                    "description": "Find emails that match a word exactly.",
                    "examples": ["+unicorn"],
                },
                {
                    "operator": "rfc822msgid",
                    "description": "Find emails with a specific message-id header.",
                    "examples": ["rfc822msgid:200503292@example.com"],
                },
                {
                    "operator": "has:userlabels",
                    "description": "Find emails that have user labels.",
                    "examples": ["has:userlabels"],
                },
                {
                    "operator": "has:nouserlabels",
                    "description": "Find emails that don't have user labels.",
                    "examples": ["has:nouserlabels"],
                },
            ]
        }
    )


@function_tool(
    auth_provider=AuthProvider.GOOGLE,
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
)
def list_gmail(q: str, **kwargs):
    """
    List gmail with gmail query

    Args:
        q(str) : gmail query, see https://support.google.com/mail/answer/7190?hl=en
                 call get_gmail_query_definition to get the definition of gmail query

    """
    token = kwargs["GOOGLE_TOKEN"]

    response = requests.get(
        url=f"https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers={
            "Authorization": f"Bearer {token}",
        },
        params={
            "q": q,
        },
    )

    if response.status_code != 200:
        return f"failed to get mail list. error : {response.text}"

    return response.json()


@function_tool(
    auth_provider=AuthProvider.GOOGLE,
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
)
def get_gmail_short_snippet(message_id: str, **kwargs):
    """
    Get a short snippet of an email message

    Args:
        message_id(str) : The ID of the email message to get a snippet of
    """
    token = kwargs["GOOGLE_TOKEN"]

    response = requests.get(
        url=f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    if response.status_code != 200:
        return f"failed to get mail snippet. error : {response.text}"

    result = response.json()
    return result["snippet"]


@function_tool(
    auth_provider=AuthProvider.GOOGLE,
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
)
def read_gmail_detail(message_id: str, **kwargs):
    """
    Read a specific email message

    Args:
        message_id(str) : The ID of the email message to read
    """
    token = kwargs["GOOGLE_TOKEN"]

    response = requests.get(
        url=f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    if response.status_code != 200:
        return f"failed to read mail. error : {response.text}"

    result = response.json()

    # truncate under 100000 token
    if len(json.dumps(result)) > 100000:
        return json.dumps(result)[:100000]


@function_tool(
    auth_provider=AuthProvider.GOOGLE,
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
)
def read_gmail_thread_detail(thread_id: str, **kwargs):
    """
    Read an entire email thread

    Args:
        thread_id(str) : The ID of the email thread to read
    """
    token = kwargs["GOOGLE_TOKEN"]

    response = requests.get(
        url=f"https://gmail.googleapis.com/gmail/v1/users/me/threads/{thread_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    if response.status_code != 200:
        return f"failed to read mail thread. error : {response.text}"

    result = response.json()

    # truncate under 100000 token
    if len(json.dumps(result)) > 100000:
        return json.dumps(result)[:100000]


@function_tool()
def get_today(**kwargs):
    return datetime.datetime.now().isoformat()


async def agent():
    pocket = PocketOpenAI(
        tools=[
            *BuiltinTools.slack(),
            get_gmail_query_definition,
            list_gmail,
            get_gmail_short_snippet,
            get_today,
            read_gmail_detail,
        ]
    )
    tool_specs = pocket.get_open_ai_tool_specs()

    model = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = []

    system_prompt = {
        "role": "system",
        "content": """
When asked, “Summarize today’s emails,” you should fetch and summarize all unread emails received today, one by one.
	1.	Use list_gmail to retrieve the list of emails.
	2.	Use get_gmail_short_snippet to fetch a short snippet for each email and summarize it for display.
	3.	Use read_gmail_detail only when the user requests more specific details about a particular email.
""",
    }

    messages.append(system_prompt)
    while True:
        print("user input(q to quit) : ", end="")
        user_input = input()
        if user_input == "q":
            break

        user_message = {"content": user_input, "role": "user"}
        messages.append(user_message)

        while True:
            response = model.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tool_specs,
            )
            choice = response.choices[0]
            messages.append(choice.message)
            if choice.finish_reason == "stop":
                break

            elif choice.finish_reason == "tool_calls":
                tool_calls = choice.message.tool_calls
                for tool_call in tool_calls:
                    print("[TOOL CALL] ", tool_call)
                    tool_message = await pocket.ainvoke(tool_call)
                    messages.append(tool_message)

        print("response : ", messages[-1].content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(agent())
