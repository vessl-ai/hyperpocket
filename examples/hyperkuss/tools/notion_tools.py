import os
from typing import Dict, List, Optional
from hyperpocket.tool import function_tool
from hyperpocket.auth import AuthProvider
from notion_client import Client
import logging

logger = logging.getLogger(__name__)

@function_tool(auth_provider=AuthProvider.NOTION)
def search_pages(
    query: str,
    filter_by: Optional[str] = None,
    sort_by: Optional[str] = None,
    **kwargs
) -> Dict:
    """
    Search Notion pages using a query string.
    Args:
        query: Search query text
        filter_by: Optional filter (database, page, or both)
        sort_by: Optional sort field (last_edited_time, created_time)
    Returns:
        List of matching pages with their details
    """
    try:
        NOTION_TOKEN = kwargs.get("NOTION_TOKEN")
        client = Client(auth=NOTION_TOKEN)
        
        response = client.search(
            query=query,
            filter={"property": "object", "value": filter_by} if filter_by else None,
            sort={"direction": "descending", "timestamp": sort_by} if sort_by else None
        )
        
        results = []
        for page in response["results"]:
            result = {
                "id": page["id"],
                "title": page.get("properties", {}).get("title", {}).get("title", [{}])[0].get("plain_text", "Untitled"),
                "url": page.get("url"),
                "created_time": page.get("created_time"),
                "last_edited_time": page.get("last_edited_time"),
                "object_type": page.get("object")
            }
            results.append(result)
        
        return {
            "results": results,
            "count": len(results),
            "message": f"Found {len(results)} matching pages"
        }
    except Exception as e:
        logger.error(f"Failed to search Notion: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to search Notion pages"
        }

@function_tool(auth_provider=AuthProvider.NOTION)
def create_page(
    title: str,
    content: str,
    parent_page_id: Optional[str] = None,
    **kwargs
) -> Dict:
    """
    Create a new Notion page.
    Args:
        title: Page title
        content: Page content in plain text
        parent_page_id: Optional parent page ID
    Returns:
        Created page details
    """
    try:
        NOTION_TOKEN = kwargs.get("NOTION_TOKEN")
        client = Client(auth=NOTION_TOKEN)

        # Prepare page content
        children = [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": content}
                }]
            }
        }]

        # Create page
        page = client.pages.create(
            parent={"type": "page_id", "page_id": parent_page_id} if parent_page_id else {"type": "workspace", "workspace": True},
            properties={
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            },
            children=children
        )

        return {
            "id": page["id"],
            "url": page["url"],
            "title": title,
            "message": "Page created successfully"
        }
    except Exception as e:
        logger.error(f"Failed to create Notion page: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to create Notion page"
        }

@function_tool(auth_provider=AuthProvider.NOTION)
def get_page_content(
    page_id: str,
    **kwargs
) -> Dict:
    """
    Get content of a Notion page.
    Args:
        page_id: ID of the page to retrieve
    Returns:
        Page content and details
    """
    try:
        NOTION_TOKEN = kwargs.get("NOTION_TOKEN")
        client = Client(auth=NOTION_TOKEN)

        # Get page metadata
        page = client.pages.retrieve(page_id=page_id)
        
        # Get page blocks (content)
        blocks = client.blocks.children.list(block_id=page_id)
        
        content = []
        for block in blocks.get("results", []):
            if block["type"] == "paragraph":
                text = block["paragraph"]["rich_text"]
                if text:
                    content.append(text[0]["plain_text"])

        return {
            "id": page["id"],
            "title": page.get("properties", {}).get("title", {}).get("title", [{}])[0].get("plain_text", "Untitled"),
            "url": page["url"],
            "content": "\n".join(content),
            "created_time": page["created_time"],
            "last_edited_time": page["last_edited_time"]
        }
    except Exception as e:
        logger.error(f"Failed to get Notion page: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to retrieve Notion page"
        } 