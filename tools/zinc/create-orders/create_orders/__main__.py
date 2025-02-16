import json
import os
import sys
import requests

from pydantic import BaseModel, Field

token = os.getenv('ZINC_TOKEN')

class ProductObject(BaseModel):
    product_id: str = Field(description="The retailer's unique identifier for the product. Note that Zinc does not support digital purchases or Amazon prime pantry items.")
    quantity: int = Field(description="The number of products to purchase.")
    seller_selection_criteria: dict = Field(description="A seller selection criteria object containing information about which offers to choose when there are multiple offers available. If the seller selection criteria object is not included for a product, the seller selection criteria will default to 'prime': true, 'handling_days_max': 6, and 'condition_in': ['New']")
    
class SellerSelectionCriteriaObject(BaseModel):
    addon: bool = Field(description="(Amazon only) Specifies whether the selected offer should be an addon item")
    buy_box: bool = Field(description="(Amazon only) Specifies whether the selected offer should be Amazon's default buy box offer")
    condition_in: list = Field(description="An array of item conditions that the Zinc API must order from")
    condition_not_in: list = Field(description="An array of item conditions that the Zinc API must not order from")
    first_party_seller: bool = Field(description="Is the seller first-party? e.g. sold by Walmart.com on walmart")
    handling_days_max: int = Field(description="The maximum number of allowable days for shipping and handling")
    international: bool = Field(description="Specifies whether the item should come from an international supplier")
    max_item_price: float = Field(description="The maximum allowable price in cents for an item")
    merchant_id_in: list = Field(description="(Amazon only) An array of merchant ids that the Zinc API must order from")
    merchant_id_not_in: list = Field(description="(Amazon only) An array of merchant ids that the Zinc API must not order from")
    min_seller_num_ratings: int = Field(description="(Amazon only) The minimum number of ratings required for an Amazon seller's offer to be selected")
    min_seller_percent_positive_feedback: float = Field(description="(Amazon only) The minimum percentage of positive ratings of an Amazon seller for their offer to be selected")
    prime: bool = Field(description="(Amazon only) Specifies whether the selected offer should be an Amazon Prime offer")
    allow_oos: bool = Field(description="(Amazon only) Specifies whether we should still attempt to complete ordering with the cheapest offer if all offers appear unavailable")
    
class ShippingObject(BaseModel):
    order_by: str = Field(description="The ordering of available shipping methods that meet the desired criteria. Available values are price or speed. If ordering by price, then the Zinc API will choose the cheapest shipping method that meets the desired criteria, while speed will choose the fastest shipping method meeting the criteria.")
    max_days: int = Field(description="The maximum number of days allowed for shipping on the order.")
    max_price: float = Field(description="The maximum price in cents allowed for the shipping cost of the order.")

class AddressObject(BaseModel):
    first_name: str = Field(description="The first name of the addressee")
    last_name: str = Field(description="The last name of the addressee")
    address_line1: str = Field(description="The house number and street name")
    address_line2: str = Field(description="The suite, post office box, or apartment number (optional)")
    zip_code: str = Field(description="The zip code of the address")
    city: str = Field(description="The city of the address")
    state: str = Field(description="The USPS abbreviation for the state of the address (e.g. AK)")
    country: str = Field(description="The ISO abbreviation for the country of the address (e.g. US). A list of all available two-letter country codes can be found here.")
    phone_number: str = Field(description="The phone number associated with the address")
    instructions: str = Field(description="Optional instructions to include with the shipping addresses")

class PaymentMethodObject(BaseModel):
    name_on_card: str = Field(description="The full name on the credit/debit card")
    number: str = Field(description="The credit/debit card number")
    security_code: str = Field(description="The card verification value on the back of the credit/debit card")
    expiration_month: int = Field(description="The month of the expiration of the card (e.g. January is 1, February is 2)")
    expiration_year: int = Field(description="The year of the expiration of the card (e.g. 2016)")
    use_gift: bool = Field(description="Whether or not to use the gift balance on the retailer account. If true, then the gift balance will be used for payment. Only works for retailers which support gift balance (Amazon and Walmart).")
    use_account_payment_defaults: bool = Field(description="Overrides all other payment_method options and uses the default payment configuration on the account. Only applies to Amazon orders.")
    is_virtual_card: bool = Field(description="Whether or not to check the 'Virtual or one-time-use' checkbox when adding the card. Only applies to Amazon orders.")
    reuse: bool = Field(description="If true, will skip entering credit card if it is already present and we aren't prompted for it. Only applies to Amazon orders.")
    
class WebhooksObject(BaseModel):
    request_succeeded: str = Field(description="The webhook URL to send data to when a request succeeds")
    order_placed: str = Field(description="(deprecated) Synonym for request_succeeded (placing orders call only)")
    request_failed: str = Field(description="The webhook URL to send data to when a request fails")
    order_failed: str = Field(description="(deprecated) Synonym for request_failed (placing orders call only)")
    tracking_obtained: str = Field(description="The webhook URL to send data to when ALL tracking for an order is retrieved (placing orders call only)")
    tracking_updated: str = Field(description="The webhook URL to send data to when ANY tracking for an order is retrieved (placing orders call only)")
    status_updated: str = Field(description="The webhook URL to send data to when the status of a request is updated")
    case_updated: str = Field(description="The webhook URL to send data to when a ZMA case associated with the order receives an update")
    
class RetailerCredentialsObject(BaseModel):
    email: str = Field(description="The email for the retailer account")
    password: str = Field(description="The password for the retailer account")
    verification_code: str = Field(description="(Optional) The verification code required by the retailer for logging in. Only required in cases where the retailer prevents a login with an account_locked_verification_required error code.")
    totp_2fa_key: str = Field(description="(Optional) The secret key used for two factor authentication. If you have two factor authentication enabled, you must provide this key. You can find the 64 digit Amazon key by enabling two factor authentication and clicking on the 'Can't scan the barcode?' link. Note: This is not the 6 digit time based code.")
    
class PromoCodeObject(BaseModel):
    code: str = Field(description="The promo code to apply (required)")
    optional: bool = Field(default=False, description="(Optional) Should we continue placing the order if this code fails to apply? Defaults to false.")
    merchant_id: str = Field(description="(Optional) If supplied, only try this code if we selected an offer from the given merchant.")
    discount_amount: float = Field(default=0, description="(Optional) Fixed amount in cents by which we should discount the matching merchant's offers during offer selection. Only makes sense if merchant_id is also supplied. Defaults to 0.")
    discount_percentage: float = Field(default=0, description="(Optional) Percentage amount (between 0 and 100) by which we should discount the matching merchant's offers during offer selection. Only makes sense if merchant_id is also supplied. Defaults to 0.")
    cost_override: float = Field(description="(Optional) If supplied, we will assume all offers by this merchant cost exactly this many cents. Only makes sense if merchant_id is also supplied. Overrides other discount methods.")

class PriceComponentsObject(BaseModel):
    shipping: float = Field(description="The price for shipping")
    products: list = Field(description="A list of the price, quantity, and seller_id for each product_id in the order")
    subtotal: float = Field(description="The total price of the order before tax and other price adjustments")
    tax: float = Field(description="The tax collected on the order")
    total: float = Field(description="The total price paid for the order in the currency specified by the currency attribute")
    gift_certificate: float = Field(default=0, description="(Optional) The amount of value used on a gift certificate placed on the account")
    currency: str = Field(description="Currency of all attributes except converted_payment_total")
    payment_currency: str = Field(description="Currency used in the payment transaction")
    converted_payment_total: float = Field(description="Total payment in payment_currency currency")

class MerchantOrderIdsObject(BaseModel):
    merchant_order_id: str = Field(description="The identifier provided by the retailer for the order that was placed")
    merchant: str = Field(description="The retailer on which the order was placed")
    account: str = Field(description="The account on which the order was placed")
    placed_at: str = Field(description="The date and time at which the order was placed")
    tracking: list = Field(description="A list of the tracking numbers associated with the order")
    product_ids: list = Field(description="A list of product_ids in the order")
    tracking_url: str = Field(description="The tracking url provided by the merchant (if available)")
    delivery_date: str = Field(description="The projected delivery date given by the retailer")

class AccountStatusObject(BaseModel):
    prime: bool = Field(description="Indicates if the account has Prime enabled")
    fresh: bool = Field(description="Indicates if the account has Fresh enabled")
    business: bool = Field(description="Indicates if the account has Business enabled")
    charity: str = Field(description="Indicates if the account has a Charity associated")

class ProductOfferObject(BaseModel):
    addon: bool = Field(description="Whether or not the product is an addon item that can only be purchased in a bundle")
    condition: str = Field(description="The condition of the product. Possible values are New, Refurbished, Used - Like New, Used - Very Good, Used - Good, Used - Acceptable, Unacceptable.")
    handling_days_max: int = Field(description="The maximum number of days required for shipping and handling")
    handling_days_min: int = Field(description="The minimum number of days required for shipping and handling")
    international: bool = Field(description="Whether or not the product ships from outside of the United States")
    offer_id: str = Field(description="(Amazon only). The unique identifier that identifies an item sold by any merchant on Amazon")
    price: float = Field(description="The price of the item, not including shipping in cents.")
    marketplace_fulfilled: bool = Field(description="Whether or not the product ships direct from retailer. For Amazon, this indicates if the item is shipped with Prime shipping.")
    seller_id: str = Field(description="The merchant's unique identifier for the product")
    seller_name: str = Field(description="The name of the seller of the current offer")
    seller_num_ratings: int = Field(description="The number of ratings that the seller has accumulated")
    seller_percent_positive: float = Field(description="Number between 0 and 100 denoting the percentage of positive ratings the seller has received")
    shipping_options: list = Field(description="A list of shipping options available for the product")
    prime_only: bool = Field(description="(Amazon only). Whether or not the product only ships using Amazon Prime")
    member_only: bool = Field(description="(Costco only) Whether or not the purchase must be from a Costco Member")

class TrackingObject(BaseModel):
    merchant_order_id: str = Field(description="The corresponding order identifier for which tracking was obtained.")
    carrier: str = Field(description="(Optional) The logistics carrier that can track the package.")
    tracking_number: str = Field(description="(Optional) The tracking number from the logistics carrier.")
    delivery_status: str = Field(description="The current tracking status. Will be 'Delivered' when the package is delivered.")
    tracking_url: str = Field(description="(Optional) The tracking url that can be used to find the carrier and tracking number for a package.")
    product_ids: list = Field(description="The list of product ids in the shipment. Product ids will be repeated if more than one of the product is in the shipment.")
    retailer_tracking_number: str = Field(description="(Amazon only) (Optional) Amazon's tracking numbers are not publicly trackable but are printed on the package so we include them here.")
    retailer_tracking_url: str = Field(description="(Optional) A url provided by the retailer than can be used to track the package.")
    obtained_at: str = Field(description="When tracking was last updated.")

class CreateOrdersRequest(BaseModel):
    retailer: str = Field(description="The retailer code of the supported retailer")
    products: list = Field(description="A list of product objects that should be ordered")
    shipping_address: AddressObject = Field(description="An address object to which the order will be delivered")
    shipping_method: str = Field(description="The desired shipping method for the object. Available methods are cheapest, fastest, amazon_day, or free. You must provide either this or the shipping attribute, but not both.")
    shipping: ShippingObject = Field(description="A shipping object with information as to which shipping method to use. You must provide either this or the shipping_method attribute, but not both.")
    billing_address: AddressObject = Field(description="An address object for the person associated with the credit card")
    payment_method: PaymentMethodObject = Field(description="A payment method object containing payment information for the order")
    retailer_credentials: RetailerCredentialsObject = Field(description="A retailer credentials object for logging into the retailer with a preexisting account")
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
        url="https://api.zinc.io/v1/orders",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json = req.model_dump(),
    )

    if response.status_code != 200:
        return f"failed to insert calendar events. error : {response.text}"

    return response.json()


def main():
    with open("schema.json", "w") as f:
        f.write(CreateOrdersRequest.schema_json(indent=2))
    print(CreateOrdersRequest.model_json_schema())
    breakpoint()
    req = json.load(sys.stdin.buffer)
    CreateOrdersRequest.model_json_schema
    req_typed = CreateOrdersRequest.model_validate(req)
    response = create_orders(req_typed)

    print(response)


if __name__ == '__main__':
    main()