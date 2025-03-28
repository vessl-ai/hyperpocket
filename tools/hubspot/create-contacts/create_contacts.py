import json
import os
import sys
from typing import List, Optional
from pydantic import BaseModel, Field
import hubspot
from pprint import pprint
from hubspot.crm.contacts import (
    BatchInputSimplePublicObjectInputForCreate,
    ApiException,
)

token = os.getenv("HUBSPOT_TOKEN")


class HubspotContact(BaseModel):
    firstname: str = Field(description="The first name of the contact to create")
    lastname: str = Field(description="The last name of the contact to create")
    email: Optional[str] = Field(description="The email of the contact to create")
    additional_properties: Optional[dict] = Field(
        description="Additional properties to create the contact with"
    )


class HubspotCreateContactsRequest(BaseModel):
    contacts: List[HubspotContact] = Field(description="The contacts to create")


def create_contacts(req: HubspotCreateContactsRequest):
    client = hubspot.Client.create(access_token="YOUR_ACCESS_TOKEN")
    inputs = [
        {
            "associations": [
                {
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 0,
                        }
                    ],
                    "to": {"id": "string"},
                }
            ],
            "objectWriteTraceId": "string",
            "properties": {
                "email": x.email,
                "lastname": x.lastname,
                "firstname": x.firstname,
            }
            if x.email
            else {
                "lastname": x.lastname,
                "firstname": x.firstname,
            },
        }
        for x in req.contacts
    ]

    for i, contact in enumerate(req.contacts):
        if contact.additional_properties:
            inputs[i]["properties"] = {
                **inputs[i]["properties"],
                **contact.additional_properties,
            }

    batch_input_simple_public_object_input_for_create = (
        BatchInputSimplePublicObjectInputForCreate(inputs=inputs)
    )

    try:
        api_response = client.crm.contacts.batch_api.create(
            batch_input_simple_public_object_input_for_create=batch_input_simple_public_object_input_for_create
        )
        pprint(api_response)

        return {"success": True, "message": "Contacts created successfully"}
    except ApiException as e:
        print("Exception when calling batch_api->create: %s\n" % e)
        return {"success": False, "message": str(e)}


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = HubspotCreateContactsRequest.model_validate(req)
    response = create_contacts(req_typed)

    print(response)


if __name__ == "__main__":
    main()
