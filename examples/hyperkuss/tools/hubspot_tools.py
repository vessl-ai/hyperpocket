import os
from typing import List, Dict, Optional
from hyperpocket.tool import function_tool
import hubspot
from hubspot.crm.contacts import ApiException

# Initialize HubSpot client
client = hubspot.Client.create(access_token=os.environ["HUBSPOT_ACCESS_TOKEN"])

@function_tool()
def search_contacts(query: str) -> List[Dict]:
    """
    Search for contacts in HubSpot using a query string.
    Args:
        query: Search query (e.g., email, name, company)
    Returns:
        List of matching contacts with their details
    """
    try:
        public_object_search_request = {
            "query": query,
            "properties": ["firstname", "lastname", "email", "company", "phone"]
        }
        response = client.crm.contacts.search_api.do_search(
            public_object_search_request=public_object_search_request
        )
        
        contacts = []
        for result in response.results:
            contact = {
                "id": result.id,
                "name": f"{result.properties.get('firstname', '')} {result.properties.get('lastname', '')}".strip(),
                "email": result.properties.get('email', ''),
                "company": result.properties.get('company', ''),
                "phone": result.properties.get('phone', '')
            }
            contacts.append(contact)
        
        return contacts
    except ApiException as e:
        return f"Error searching contacts: {str(e)}"

@function_tool()
def create_contact(
    email: str,
    firstname: Optional[str] = None,
    lastname: Optional[str] = None,
    company: Optional[str] = None,
    phone: Optional[str] = None
) -> Dict:
    """
    Create a new contact in HubSpot.
    Args:
        email: Contact's email address (required)
        firstname: Contact's first name
        lastname: Contact's last name
        company: Contact's company name
        phone: Contact's phone number
    Returns:
        Created contact details
    """
    try:
        properties = {
            "email": email
        }
        if firstname:
            properties["firstname"] = firstname
        if lastname:
            properties["lastname"] = lastname
        if company:
            properties["company"] = company
        if phone:
            properties["phone"] = phone

        response = client.crm.contacts.basic_api.create(
            simple_public_object_input_for_create={"properties": properties}
        )
        
        return {
            "id": response.id,
            "properties": response.properties,
            "message": "Contact created successfully"
        }
    except ApiException as e:
        return f"Error creating contact: {str(e)}"

@function_tool()
def get_contact_by_id(contact_id: str) -> Dict:
    """
    Get contact details by ID.
    Args:
        contact_id: HubSpot contact ID
    Returns:
        Contact details
    """
    try:
        response = client.crm.contacts.basic_api.get_by_id(
            contact_id=contact_id,
            properties=["firstname", "lastname", "email", "company", "phone"]
        )
        
        return {
            "id": response.id,
            "name": f"{response.properties.get('firstname', '')} {response.properties.get('lastname', '')}".strip(),
            "email": response.properties.get('email', ''),
            "company": response.properties.get('company', ''),
            "phone": response.properties.get('phone', '')
        }
    except ApiException as e:
        return f"Error getting contact: {str(e)}" 