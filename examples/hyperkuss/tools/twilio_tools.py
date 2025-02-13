import os
from typing import Dict
from hyperpocket.tool import function_tool
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)

# Initialize Twilio client
client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])

@function_tool()
def send_sms(
    to_number: str,
    message: str,
    from_number: str = os.environ.get("TWILIO_PHONE_NUMBER")
) -> Dict:
    """
    Send an SMS message using Twilio.
    Args:
        to_number: The phone number to send SMS to (E.164 format, e.g., +1234567890)
        message: The message content to send
        from_number: The Twilio phone number to send from (defaults to configured number)
    Returns:
        Message details including status and message SID
    """
    try:
        # Send the message
        message = client.messages.create(
            to=to_number,
            from_=from_number,
            body=message
        )

        logger.info(f"Sent SMS to {to_number} with SID: {message.sid}")
        return {
            "status": message.status,
            "message_sid": message.sid,
            "from": message.from_,
            "to": message.to,
            "message": "SMS sent successfully"
        }
    except Exception as e:
        logger.error(f"Failed to send SMS: {str(e)}")
        return {
            "error": str(e),
            "message": (
                "Failed to send SMS. If you're using a trial account, "
                "make sure the number is verified in the Twilio console."
            )
        }

@function_tool()
def make_phone_call(
    to_number: str,
    message: str,
    from_number: str = os.environ.get("TWILIO_PHONE_NUMBER")
) -> Dict:
    """
    Make an outbound phone call using Twilio.
    Args:
        to_number: The phone number to call (E.164 format, e.g., +1234567890)
        message: The message to be spoken during the call
        from_number: The Twilio phone number to call from (defaults to configured number)
    Returns:
        Call details including status and call SID
    """
    try:
        # Check if number is verified (for trial accounts)
        verified_numbers = client.outgoing_caller_ids.list()
        verified_numbers = [number.phone_number for number in verified_numbers]
        
        if to_number not in verified_numbers:
            return {
                "error": "Unverified number",
                "message": (
                    "This number is not verified. In trial mode, you can only call verified numbers. "
                    "Please verify the number first in the Twilio console or upgrade your account. "
                    f"Currently verified numbers: {', '.join(verified_numbers) if verified_numbers else 'None'}"
                )
            }

        # Create TwiML to speak the message
        twiml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say>{message}</Say>
            <Pause length="2"/>
            <Say>This was an automated call from VESSL AI. Goodbye.</Say>
        </Response>
        """

        # Make the call
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            twiml=twiml
        )

        logger.info(f"Initiated call to {to_number} with SID: {call.sid}")
        return {
            "status": call.status,
            "call_sid": call.sid,
            "from": call.from_,
            "to": call.to,
            "message": "Call initiated successfully"
        }
    except Exception as e:
        logger.error(f"Failed to make call: {str(e)}")
        return {
            "error": str(e),
            "message": (
                "Failed to initiate call. If you're using a trial account, "
                "make sure the number is verified in the Twilio console."
            )
        }

@function_tool()
def check_call_status(call_sid: str) -> Dict:
    """
    Check the status of a previously initiated call.
    Args:
        call_sid: The SID of the call to check
    Returns:
        Current call status and details
    """
    try:
        call = client.calls(call_sid).fetch()
        return {
            "status": call.status,
            "duration": call.duration,
            "start_time": str(call.start_time),
            "end_time": str(call.end_time) if call.end_time else None,
            "direction": call.direction,
            "answered_by": call.answered_by
        }
    except Exception as e:
        logger.error(f"Failed to fetch call status: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to fetch call status"
        }

@function_tool()
def verify_phone_number(phone_number: str) -> Dict:
    """
    Start the verification process for a phone number with Twilio.
    Args:
        phone_number: The phone number to verify (E.164 format, e.g., +1234567890)
    Returns:
        Verification status and instructions
    """
    try:
        # Start verification process
        validation_request = client.validation_requests.create(
            phone_number=phone_number,
            friendly_name="VESSL AI Bot"
        )
        
        return {
            "status": "verification_initiated",
            "message": (
                "Verification process started. You will receive a call from Twilio. "
                "Answer the call and enter the validation code shown in the Twilio console. "
                f"Validation code will be sent to: {phone_number}"
            ),
            "validation_code": validation_request.validation_code
        }
    except Exception as e:
        logger.error(f"Failed to start verification: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to start phone number verification process"
        }

@function_tool()
def list_verified_numbers() -> Dict:
    """
    List all currently verified phone numbers.
    Returns:
        List of verified phone numbers
    """
    try:
        verified_numbers = client.outgoing_caller_ids.list()
        numbers = [
            {
                "phone_number": number.phone_number,
                "friendly_name": number.friendly_name,
                "verified": True
            } for number in verified_numbers
        ]
        
        return {
            "verified_numbers": numbers,
            "count": len(numbers),
            "message": f"Found {len(numbers)} verified numbers"
        }
    except Exception as e:
        logger.error(f"Failed to list verified numbers: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to fetch verified numbers"
        } 