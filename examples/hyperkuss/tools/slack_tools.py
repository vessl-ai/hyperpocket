from typing import Dict, List, Optional
from hyperpocket.tool import function_tool
from slack_sdk import WebClient
import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

@function_tool()
def get_mention_messages(
    mention_user: str,
    days_back: int = 7,
    max_results: int = 100,
    **kwargs
) -> Dict:
    """
    Get recent Slack messages that mention a specific user in public channels, including thread replies.
    Args:
        mention_user: Username or user ID to search for (e.g., "@john" or "U1234567")
        days_back: Number of days to look back (default: 7)
        max_results: Maximum number of messages to return (default: 100)
    Returns:
        List of messages with thread replies from public channels
    """
    try:
        SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        client = WebClient(token=SLACK_TOKEN)
        
        # Convert username to ID if needed
        if mention_user.startswith("@"):
            user_info = client.users_lookupByEmail(email=mention_user[1:])
            mention_user = user_info["user"]["id"]
        
        # Calculate time range
        oldest_time = (datetime.now() - timedelta(days=days_back)).timestamp()
        
        # Get only public channels
        channels = []
        cursor = None
        while True:
            response = client.conversations_list(
                types="public_channel",  # Only public channels
                exclude_archived=True,
                cursor=cursor
            )
            channels.extend(response["channels"])
            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        # Search for messages in each channel
        all_messages = []
        for channel in channels:
            try:
                # Get messages in channel
                response = client.conversations_history(
                    channel=channel["id"],
                    oldest=oldest_time,
                    limit=max_results
                )
                
                for msg in response["messages"]:
                    # Check if message mentions the user
                    if (f"<@{mention_user}>" in msg.get("text", "") or 
                        mention_user in msg.get("text", "")):
                        
                        # Get thread replies if any
                        thread_replies = []
                        if msg.get("thread_ts"):
                            thread = client.conversations_replies(
                                channel=channel["id"],
                                ts=msg["thread_ts"]
                            )
                            thread_replies = thread["messages"][1:]  # Skip parent message
                        
                        message_data = {
                            "channel_name": channel["name"],
                            "channel_id": channel["id"],
                            "channel_type": "public",  # Added channel type
                            "timestamp": msg["ts"],
                            "text": msg["text"],
                            "user": msg.get("user"),
                            "thread_replies": [{
                                "user": reply.get("user"),
                                "text": reply.get("text"),
                                "timestamp": reply.get("ts")
                            } for reply in thread_replies],
                            "permalink": client.chat_getPermalink(
                                channel=channel["id"],
                                message_ts=msg["ts"]
                            )["permalink"]
                        }
                        all_messages.append(message_data)
                        
            except Exception as e:
                logger.error(f"Error fetching messages from channel {channel['name']}: {str(e)}")
                continue

        # Sort messages by timestamp
        all_messages.sort(key=lambda x: float(x["timestamp"]), reverse=True)
        
        return {
            "messages": all_messages[:max_results],
            "count": len(all_messages[:max_results]),
            "time_range": f"Last {days_back} days",
            "message": f"Found {len(all_messages)} public channel messages mentioning {mention_user}"
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch mention messages: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to fetch Slack messages"
        } 