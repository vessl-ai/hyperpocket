import os
from typing import List, Dict, Optional
from hyperpocket.tool import function_tool
import hubspot
from hubspot.crm.contacts import ApiException
from hyperpocket.auth import AuthProvider
import logging

logger = logging.getLogger(__name__)

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

@function_tool()
def list_deals(
    max_results: int = 50,
    stage: Optional[str] = None,
    **kwargs
) -> Dict:
    """
    Get list of deals from HubSpot with optional stage filter.
    Args:
        max_results: Maximum number of deals to return (default: 50)
        stage: Filter by deal stage (e.g., 'closedwon', 'closedlost', 'appointmentscheduled')
    Returns:
        List of deals with basic information
    """
    try:
        access_token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
        if not access_token:
            raise ValueError("HubSpot access token not found in environment")
            
        client = hubspot.Client.create(access_token=access_token)
        
        # Build filter if stage is provided
        filter_groups = []
        if stage:
            filter_groups = [{
                "filters": [{
                    "propertyName": "dealstage",
                    "operator": "EQ",
                    "value": stage
                }]
            }]
        
        # Search request
        public_object_search_request = {
            "filter_groups": filter_groups,
            "properties": [
                "dealname",
                "amount",
                "dealstage",
                "closedate",
                "pipeline",
                "company"
            ],
            "limit": max_results,
            "sorts": [{"propertyName": "createdate", "direction": "DESCENDING"}]
        }
        
        response = client.crm.deals.search_api.do_search(
            public_object_search_request=public_object_search_request
        )
        
        deals = [{
            'id': deal.id,
            'name': deal.properties.get('dealname'),
            'amount': deal.properties.get('amount'),
            'stage': deal.properties.get('dealstage'),
            'close_date': deal.properties.get('closedate'),
            'pipeline': deal.properties.get('pipeline'),
            'company': deal.properties.get('company')
        } for deal in response.results]
        
        return {
            "deals": deals,
            "count": len(deals),
            "message": f"Found {len(deals)} deals" + (f" in stage '{stage}'" if stage else "")
        }
        
    except Exception as e:
        logger.error(f"Error listing deals: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to list deals"
        }

@function_tool()
def get_deal_details(
    query: str,
    include_contacts: bool = True,
    include_notes: bool = True,
    include_emails: bool = True,
    **kwargs
) -> Dict:
    """
    Get comprehensive deal details by deal ID, deal name, or company name.
    Args:
        query: Deal ID, deal name, or company name to search for
        include_contacts: Include associated contacts (default: True)
        include_notes: Include deal notes (default: True)
        include_emails: Include email communications (default: True)
    Returns:
        Deal details and associated information
    """
    try:
        access_token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
        if not access_token:
            raise ValueError("HubSpot access token not found in environment")
            
        client = hubspot.Client.create(access_token=access_token)
        
        # First try to get deal directly if query looks like an ID
        try:
            if query.isdigit():
                return get_deal_by_id(
                    client, 
                    query, 
                    include_contacts, 
                    include_notes, 
                    include_emails
                )
        except:
            pass
        
        # Search for deals by name or company
        filter_groups = [{
            "filters": [{
                "propertyName": "dealname",
                "operator": "CONTAINS_TOKEN",
                "value": query
            }]
        }, {
            "filters": [{
                "propertyName": "company",
                "operator": "CONTAINS_TOKEN",
                "value": query
            }]
        }]
        
        public_object_search_request = {
            "filter_groups": filter_groups,
            "properties": ["dealname", "amount", "dealstage", "createdate", "closedate", "company"],
            "limit": 5  # Limit search results
        }
        
        response = client.crm.deals.search_api.do_search(
            public_object_search_request=public_object_search_request
        )
        
        if not response.results:
            return {
                "message": f"No deals found matching '{query}'"
            }
        
        # Get full details for the first matching deal
        deal_id = response.results[0].id
        return get_deal_by_id(
            client, 
            deal_id, 
            include_contacts, 
            include_notes, 
            include_emails
        )
        
    except Exception as e:
        logger.error(f"Error getting deal details: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to get deal details"
        }

def get_deal_by_id(client, deal_id, include_contacts, include_notes, include_emails):
    """Helper function to get deal details by ID"""
    # Get basic deal info
    deal = client.crm.deals.basic_api.get_by_id(
        deal_id,
        properties=["dealname", "amount", "dealstage", "createdate", "closedate", "company"]
    )
    
    result = {
        'id': deal.id,
        'name': deal.properties.get('dealname'),
        'company': deal.properties.get('company'),
        'amount': deal.properties.get('amount'),
        'stage': deal.properties.get('dealstage'),
        'create_date': deal.properties.get('createdate'),
        'close_date': deal.properties.get('closedate')
    }
    
    # Get associated data
    if include_contacts:
        batch_input = {"inputs": [{"id": deal_id}]}
        contacts_response = client.crm.associations.batch_api.read(
            from_object_type="deals",
            to_object_type="contacts",
            batch_input_public_object_id=batch_input
        )
        
        contact_ids = []
        for res in contacts_response.results:
            contact_ids.extend([{"id": to_object.id} for to_object in res.to])
        
        if contact_ids:
            batch_read_input = {"inputs": contact_ids, "properties": ["email", "firstname", "lastname"]}
            contacts = client.crm.contacts.batch_api.read(
                batch_read_input_simple_public_object_id=batch_read_input
            )
            result['contacts'] = [{
                'id': contact.id,
                'email': contact.properties.get('email'),
                'name': f"{contact.properties.get('firstname', '')} {contact.properties.get('lastname', '')}".strip()
            } for contact in contacts.results]
    
    # Get notes if requested
    if include_notes:
        batch_input = {"inputs": [{"id": deal_id}]}
        notes_response = client.crm.associations.batch_api.read(
            from_object_type="deals",
            to_object_type="notes",
            batch_input_public_object_id=batch_input
        )
        
        note_ids = []
        for res in notes_response.results:
            note_ids.extend([{"id": to_object.id} for to_object in res.to])
        
        if note_ids:
            batch_read_input = {"inputs": note_ids, "properties": ["hs_note_body", "hs_createdate"]}
            notes = client.crm.objects.notes.batch_api.read(
                batch_read_input_simple_public_object_id=batch_read_input
            )
            result['notes'] = [{
                'id': note.id,
                'content': note.properties.get('hs_note_body'),
                'date': note.properties.get('hs_createdate')
            } for note in notes.results]
    
    # Get emails if requested
    if include_emails:
        batch_input = {"inputs": [{"id": deal_id}]}
        emails_response = client.crm.associations.batch_api.read(
            from_object_type="deals",
            to_object_type="emails",
            batch_input_public_object_id=batch_input
        )
        
        email_ids = []
        for res in emails_response.results:
            email_ids.extend([{"id": to_object.id} for to_object in res.to])
        
        if email_ids:
            batch_read_input = {
                "inputs": email_ids,
                "properties": [
                    "hs_email_subject",
                    "hs_email_text",
                    "hs_email_status",
                    "hs_timestamp"
                ]
            }
            emails = client.crm.objects.emails.batch_api.read(
                batch_read_input_simple_public_object_id=batch_read_input
            )
            result['emails'] = [{
                'id': email.id,
                'subject': email.properties.get('hs_email_subject'),
                'content': email.properties.get('hs_email_text'),
                'status': email.properties.get('hs_email_status'),
                'timestamp': email.properties.get('hs_timestamp')
            } for email in emails.results]
    
    return {
        "deal": result,
        "message": f"Retrieved deal details for '{result['name']}'"
    }

@function_tool()
def search_companies(
    query: str,
    max_results: int = 10,
    **kwargs
) -> Dict:
    """
    Search for companies in HubSpot by name.
    Args:
        query: Company name to search for
        max_results: Maximum number of results to return (default: 10)
    Returns:
        List of matching companies
    """
    try:
        access_token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
        if not access_token:
            raise ValueError("HubSpot access token not found in environment")
            
        client = hubspot.Client.create(access_token=access_token)
        
        filter_groups = [{
            "filters": [{
                "propertyName": "name",
                "operator": "CONTAINS_TOKEN",
                "value": query
            }]
        }]
        
        public_object_search_request = {
            "filter_groups": filter_groups,
            "properties": ["name", "domain", "industry", "website"],
            "limit": max_results
        }
        
        response = client.crm.companies.search_api.do_search(
            public_object_search_request=public_object_search_request
        )
        
        companies = [{
            'id': company.id,
            'name': company.properties.get('name'),
            'domain': company.properties.get('domain'),
            'industry': company.properties.get('industry'),
            'website': company.properties.get('website')
        } for company in response.results]
        
        return {
            "companies": companies,
            "count": len(companies),
            "message": f"Found {len(companies)} companies matching '{query}'"
        }
        
    except Exception as e:
        logger.error(f"Error searching companies: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to search companies"
        } 