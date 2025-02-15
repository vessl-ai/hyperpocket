import json
import os
import sys
import requests

from pydantic import BaseModel, Field

token = os.getenv('ZINC_TOKEN')


class CreateOrdersRequest(BaseModel):
    retailer: str = Field(description="The retailer code of the supported retailer")
    products: list = Field(description="A list of product objects that should be ordered")
    shipping_address: dict = Field(description="An address object to which the order will be delivered")
    shipping_method: str = Field(description="The desired shipping method for the object. Available methods are cheapest, fastest, amazon_day, or free. You must provide either this or the shipping attribute, but not both.")
    shipping: dict = Field(description="A shipping object with information as to which shipping method to use. You must provide either this or the shipping_method attribute, but not both.")
    billing_address: dict = Field(description="An address object for the person associated with the credit card")
    payment_method: dict = Field(description="A payment method object containing payment information for the order")
    retailer_credentials: dict = Field(description="A retailer credentials object for logging into the retailer with a preexisting account")
    is_gift: bool = Field(description="Whether or not this order should be placed as a gift. Typically, retailers will exclude the price of the items on the receipt if this is set.")
    max_price: float = Field(description="The maximum price in cents for the order. If the final price exceeds this number, the order will not go through and will return a max_price_exceeded error.")


def create_orders(req: CreateOrdersRequest):
    """
    Example of tool function
    response = requests.delete(
        url=f"https://www.googleapis.com/calendar/v3/calendars/{req.calendar_id}/events/{req.event_id}",
        params={
            "sendUpdates": req.send_updates
        },
        headers={
            "Authorization": f"Bearer {token}",
        }
    )

    if response.status_code != 200:
        return f"failed to delete calendar events. error : {response.text}"

    return f"successfully deleted calendar events {req.event_id}"
    """
    response = requests.post(
        url="https://api.notion.com/v1/search",
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
        },
        json = req.model_dump(),
    )

    if response.status_code != 200:
        return f"failed to insert calendar events. error : {response.text}"

    return response.json()


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = CreateOrdersRequest.model_validate(req)
    response = create_orders(req_typed)

    print(response)


if __name__ == '__main__':
    main()