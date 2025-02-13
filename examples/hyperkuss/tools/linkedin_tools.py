from typing import Dict, Optional
from hyperpocket.tool import function_tool
import requests
import logging
import os

logger = logging.getLogger(__name__)

@function_tool()
def get_profile_info(
    **kwargs
) -> Dict:
    """
    Get current user's LinkedIn profile information.
    Returns:
        Profile details including basic info and email
    """
    try:
        access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
        if not access_token:
            raise ValueError("LinkedIn access token not found in environment")

        # Get basic profile info
        profile_response = requests.get(
            "https://api.linkedin.com/v2/me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        profile_response.raise_for_status()
        profile = profile_response.json()

        # Get email address
        email_response = requests.get(
            "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        email_response.raise_for_status()
        email_data = email_response.json()
        
        email = email_data.get('elements', [{}])[0].get('handle~', {}).get('emailAddress')

        result = {
            "id": profile.get("id"),
            "firstName": profile.get("localizedFirstName"),
            "lastName": profile.get("localizedLastName"),
            "email": email
        }

        return {
            "profile": result,
            "message": "Retrieved LinkedIn profile information"
        }

    except Exception as e:
        logger.error(f"Error getting LinkedIn profile: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to get LinkedIn profile"
        } 