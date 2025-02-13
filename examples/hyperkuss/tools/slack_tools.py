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

@function_tool()
def summarize_thread(
    channel_id: str,
    thread_ts: str,
    **kwargs
) -> Dict:
    """
    Summarize all messages in a Slack thread.
    Args:
        channel_id: Channel ID containing the thread
        thread_ts: Thread timestamp ID
    Returns:
        Summary of the thread discussion
    """
    try:
        SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        client = WebClient(token=SLACK_TOKEN)
        
        # Get thread messages
        response = client.conversations_replies(
            channel=channel_id,
            ts=thread_ts
        )
        
        if not response["messages"]:
            return {
                "message": "No messages found in thread"
            }
            
        # Prepare messages for summarization
        messages = []
        for msg in response["messages"]:
            # Get user info
            user_info = client.users_info(user=msg["user"])
            username = user_info["user"]["real_name"]
            
            messages.append({
                "user": username,
                "text": msg["text"],
                "timestamp": msg["ts"]
            })
            
        # Create summary prompt
        thread_text = "\n".join([f"{m['user']}: {m['text']}" for m in messages])
        summary_prompt = f"Please summarize this Slack thread discussion:\n\n{thread_text}"
        
        # Get summary using OpenAI
        response = client.llm.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a helpful assistant that summarizes Slack discussions concisely."
            }, {
                "role": "user",
                "content": summary_prompt
            }],
            temperature=0.7
        )
        
        summary = response.choices[0].message.content
        
        return {
            "summary": summary,
            "message_count": len(messages),
            "participants": list(set(m["user"] for m in messages)),
            "message": summary
        }
        
    except Exception as e:
        logger.error(f"Failed to summarize thread: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to summarize thread"
        }

@function_tool()
def help_with_thread(
    channel_id: str,
    thread_ts: str,
    language: str = "en",
    **kwargs
) -> Dict:
    """
    Analyze current thread and provide help with ongoing discussion.
    Args:
        channel_id: Channel ID containing the thread
        thread_ts: Thread timestamp ID
        language: Response language ("en" or "ko", default: "en")
    Returns:
        Analysis and suggestions for the current discussion
    """
    try:
        SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
        client = WebClient(token=SLACK_TOKEN)
        
        # Get thread messages
        response = client.conversations_replies(
            channel=channel_id,
            ts=thread_ts
        )
        
        if not response["messages"]:
            return {
                "message": "스레드에서 메시지를 찾을 수 없습니다" if language == "ko" else "No messages found in thread"
            }
            
        # Prepare messages for analysis
        messages = []
        for msg in response["messages"]:
            user_info = client.users_info(user=msg["user"])
            username = user_info["user"]["real_name"]
            
            messages.append({
                "user": username,
                "text": msg["text"],
                "timestamp": msg["ts"]
            })
            
        # Create analysis prompt
        thread_text = "\n".join([f"{m['user']}: {m['text']}" for m in messages])
        
        system_prompt = {
            "en": """You are a helpful assistant that analyzes ongoing Slack discussions to provide immediate help.
Focus on:
1. Understanding the current situation/problem
2. Identifying what help is needed
3. Suggesting immediate next steps or solutions
4. Offering relevant tools or resources""",
            "ko": """진행 중인 Slack 토론을 분석하여 즉각적인 도움을 제공하는 도우미입니다.
다음 사항에 중점을 둡니다:
1. 현재 상황/문제 파악
2. 필요한 도움 식별
3. 즉각적인 다음 단계나 해결책 제안
4. 관련 도구나 리소스 제공"""
        }[language]
        
        user_prompt = {
            "en": f"""Please help with this ongoing discussion:

Current Thread:
{thread_text}

Provide:
1. Current Situation: What's happening now?
2. Help Needed: What kind of help is required?
3. Next Steps: What should be done next?
4. Tools/Resources: What tools or resources could help?""",
            "ko": f"""현재 진행 중인 토론에 도움을 제공해주세요:

현재 스레드:
{thread_text}

다음 사항을 제공해주세요:
1. 현재 상황: 지금 무슨 일이 일어나고 있나요?
2. 필요한 도움: 어떤 종류의 도움이 필요한가요?
3. 다음 단계: 다음에 무엇을 해야 하나요?
4. 도구/리소스: 어떤 도구나 리소스가 도움될 수 있나요?"""
        }[language]
        
        # Get analysis using OpenAI
        response = client.llm.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": system_prompt
            }, {
                "role": "user",
                "content": user_prompt
            }],
            temperature=0.7
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "analysis": analysis,
            "message_count": len(messages),
            "participants": list(set(m["user"] for m in messages)),
            "message": analysis
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze thread: {str(e)}")
        error_msg = "스레드 분석에 실패했습니다" if language == "ko" else "Failed to analyze thread"
        return {
            "error": str(e),
            "message": error_msg
        } 