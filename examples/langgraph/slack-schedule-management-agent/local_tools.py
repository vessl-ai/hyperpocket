from datetime import datetime, timezone, timedelta

from github import GithubException, Github
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from hyperpocket.auth import AuthProvider
from hyperpocket.tool import function_tool


def _get_user_id_by_nickname(user_name, client):
    try:
        # 모든 사용자 가져오기
        response = client.users_list()
        users = response.get("members", [])

        # 닉네임 부분 일치 검색
        user_name = user_name.lower()
        matched = []
        for user in users:
            if user.get("deleted", False) or user.get("is_bot", False) or user.get("is_app_user", False):
                continue

            profile = user.get("profile", {})
            # Display name 또는 real name에서 검색

            if user_name == profile.get("display_name", "").lower() \
                    or user_name == profile.get("first_name", "").lower() \
                    or user_name == profile.get("real_name", "").lower() \
                    or user_name == user.get("name", "").lower():
                matched.append(user["id"])

        if len(matched) > 1:
            return f"Duplicated user name. id list : {matched}"
        if len(matched) == 0:
            return f"Not found user name. user name : {user_name}"

        return matched[0]
    except SlackApiError as e:
        print(f"Error fetching users: {e.response['error']}, {e}")
        return None


@function_tool(
    auth_provider=AuthProvider.SLACK,
    scopes=["channels:history", "channels:read", "im:history", "mpim:history", "groups:history",
            "groups:read", "reactions:read", "mpim:read", "im:read", "users:read"],
)
def get_user_slack_threads(user_name: str, channel_name: str, range_days: int = 7, **kwargs):
    """
    get threads in time range written by user

    Args:
        user_name(str) : slack username
        channel_name(str) : slack channel name
        range_days(int) : the range to lookup thread. default: 7 days
    """

    try:
        client = WebClient(token=kwargs["SLACK_BOT_TOKEN"])

        user_id = _get_user_id_by_nickname(user_name, client)

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        ref_timestamp = (today - timedelta(days=range_days)).timestamp()

        # 모든 채널 가져오기
        channels = []
        cursor = None
        for _ in range(100):
            channels_response = client.conversations_list(cursor=cursor,
                                                          types="public_channel,private_channel,mpim,im",
                                                          exclude_archived=True, limit=100)
            cursor = channels_response["response_metadata"]["next_cursor"]
            channels.extend(channels_response.get("channels", []))

            if cursor is None or cursor == "":
                break

        user_threads = []

        for channel in channels:
            if channel.get('name', '') != channel_name:
                continue

            # 채널 ID 가져오기
            channel_id = channel["id"]

            # 채널의 메시지 가져오기
            messages = []
            cursor = None
            for _ in range(100):
                messages_response = client.conversations_history(
                    cursor=cursor, channel=channel_id, oldest=str(ref_timestamp), limit=100)
                messages.extend(messages_response.get("messages", []))
                cursor = messages_response.get("response_metadata", {}).get("next_cursor", None)

                if cursor is None or cursor == "":
                    break

            for message in messages:
                message_ts = float(message["ts"])
                if message_ts < ref_timestamp:
                    continue

                # 사용자가 작성한 쓰레드
                if message.get("user") == user_id:
                    user_threads.append(message)

        return user_threads

    except SlackApiError as e:
        print(f"Error fetching conversations: {e.response['error']}")
        return f"Error fetching conversations: {e.response['error']}"


@function_tool(
    auth_provider=AuthProvider.GITHUB,
    auth_handler="github-token"
)
def fetch_user_prs_from_organization(organization_name: str, **kwargs):
    """
    fetch user pr list from github organization

    Args:
        organization_name(str) : the organization name to fetch user's pr
    """

    try:
        # Authenticate with GitHub
        g = Github(kwargs["GITHUB_TOKEN"])
        user = g.get_user()
        org = g.get_organization(organization_name)

        # Get all repositories in the organization
        repos = org.get_repos()

        # Initialize a dictionary to store PRs by repository
        pr_list_by_repo = {}

        # Iterate over repositories
        for repo in repos:
            # Fetch pull requests created by the authenticated user
            prs = repo.get_pulls(sort='created', state="open")
            user_prs = [pr for pr in prs if pr.user.login == user.login]

            # Add to the dictionary if there are PRs for this repo
            if user_prs:
                pr_list_by_repo[repo.name] = user_prs

        return pr_list_by_repo
    except GithubException as e:
        print(f"error fetching user prs from github. error : {e}")
        return f"error fetching user prs from github. error : {e}"
