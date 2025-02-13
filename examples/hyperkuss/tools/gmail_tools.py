from typing import Dict, List, Optional
from hyperpocket.tool import function_tool
from hyperpocket.auth import AuthProvider
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
import logging
import json

logger = logging.getLogger(__name__)

@function_tool(auth_provider=AuthProvider.GOOGLE)
def get_email_conversations(
    contacts: List[str],
    max_results: int = 100,
    days_back: int = 30,
    **kwargs
) -> Dict:
    """
    Get email conversations with specified contacts.
    Args:
        contacts: List of email addresses to filter conversations
        max_results: Maximum number of conversations to return (default: 100)
        days_back: Number of days to look back (default: 30)
    Returns:
        List of email conversations
    """
    try:
        # Get credentials from kwargs
        google_creds = kwargs.get("GOOGLE_CREDENTIALS")
        if not google_creds:
            raise ValueError("Google credentials not found")

        # Create credentials object from token
        creds = Credentials.from_authorized_user_info(json.loads(google_creds))
        
        # Create Gmail API service
        service = build('gmail', 'v1', credentials=creds)
        
        # Calculate date range
        after_date = (datetime.datetime.now() - datetime.timedelta(days=days_back)).strftime('%Y/%m/%d')
        
        # Build query
        query = f"after:{after_date} AND ("
        query += " OR ".join([f"from:{email} OR to:{email}" for email in contacts])
        query += ")"
        
        # Get messages matching query
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get('messages', [])
        conversations = []

        for msg in messages:
            # Get full message details
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            to_email = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            conversations.append({
                'id': message['id'],
                'thread_id': message['threadId'],
                'subject': subject,
                'from': from_email,
                'to': to_email,
                'date': date,
                'snippet': message['snippet']
            })

        return {
            "conversations": conversations,
            "count": len(conversations),
            "message": f"Found {len(conversations)} email conversations"
        }
            
    except Exception as e:
        logger.error(f"Error getting email conversations: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to get email conversations"
        } 