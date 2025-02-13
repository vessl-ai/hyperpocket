from typing import Dict, Optional
from hyperpocket.tool import function_tool
import requests
from urllib.parse import urlparse
import logging
import os

logger = logging.getLogger(__name__)

@function_tool()
def get_deal_info(
    deal_url: str,
    **kwargs
) -> Dict:
    """
    Get deal information from Attio using the deal URL.
    Args:
        deal_url: URL like 'https://app.attio.com/workspace/deals/deal_id'
    Returns:
        Deal details and associated information
    """
    try:
        api_key = os.environ.get("ATTIO_API_KEY")
        if not api_key:
            raise ValueError("Attio API key not found in environment")

        # Parse deal ID from URL
        path_parts = urlparse(deal_url).path.split('/')
        deal_id = path_parts[-1]

        # Make API request
        response = requests.get(
            f"https://api.attio.com/v2/deals/{deal_id}",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        deal = response.json().get('data', {})

        result = {
            'deal_id': deal_id,
            'contact_email': deal.get('contact', {}).get('email'),
            'status': deal.get('status'),
            'company_name': deal.get('company', {}).get('name')
        }

        return {
            "deal": result,
            "message": f"Retrieved deal information for {deal_id}"
        }

    except Exception as e:
        logger.error(f"Error getting Attio deal: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to get deal information"
        }

@function_tool()
def list_workspace_objects(
    **kwargs
) -> Dict:
    """
    Get a list of available objects in the Attio workspace.
    Returns:
        List of objects and their details
    """
    try:
        api_key = os.environ.get("ATTIO_API_KEY")
        if not api_key:
            raise ValueError("Attio API key not found in environment")

        response = requests.get(
            "https://api.attio.com/v2/objects",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        
        objects = response.json().get('data', [])

        return {
            "objects": objects,
            "count": len(objects),
            "message": f"Found {len(objects)} objects in workspace"
        }

    except Exception as e:
        logger.error(f"Error listing Attio objects: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to list workspace objects"
        } 