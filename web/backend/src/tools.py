import base64
import glob
import io
import mimetypes
import os
import os.path
import pathlib
import time
from ast import literal_eval
from email.message import EmailMessage
from time import sleep

import pyautogui
import requests
from PIL import Image
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from hyperpocket.auth import AuthProvider
from hyperpocket.tool import function_tool

# Constants
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
PHOTO_RECENT_THRESHOLD = 10  # seconds
EMAIL_TEMPLATE = """
Thank you for stopping by the Hyperpocket booth!

For more information about Hyperpocket, please check out the links:
- GitHub Repository: https://github.com/vessl-ai/hyperpocket
- Hyperpocket Documentation: https://vessl-ai.github.io/hyperpocket/index.html
- LinkedIn: https://bit.ly/hyperpocket-linkedin

We love hearing from our users. Any feedback, questions, or cool ideas are always welcomed!
To chat with us: https://bit.ly/vesslai-hyperpocket

Best, 
Hyperpocket team
"""

SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=SLACK_TOKEN)

class ImageUtils:
    @staticmethod
    def encode_image(image_data: bytes) -> str:
        """Encode image bytes to base85 string."""
        return str(base64.b85encode(image_data))

    @staticmethod
    def decode_image(encoded_string: str) -> Image.Image:
        """Decode base85 string to PIL Image."""
        byte_image = literal_eval(encoded_string)
        decoded = base64.b85decode(byte_image)
        return Image.open(io.BytesIO(decoded))

class GmailService:
    @staticmethod
    def get_credentials():
        """Get or refresh Gmail API credentials."""
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", GMAIL_SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        
        return creds

class SlackTools:
    @staticmethod
    def format_messages(messages):
        """Format slack messages for readability."""
        formatted = []
        for msg in messages:
            text = msg.get("text", "")
            user = msg.get("user", "unknown")
            ts = msg.get("ts", "")
            formatted.append(f"[{user}]: {text} (at {ts})")
        return "\n".join(formatted)

@function_tool
def get_encoded_image_from_path(path: str) -> str:
    """Get Base64 encoded string of image from path."""
    with open(path, "rb") as img:
        return ImageUtils.encode_image(img.read())

@function_tool
def save_base64_encoded_image(path: str, encoded_image: str):
    """Save base64 encoded image to path."""
    decoded_image = ImageUtils.decode_image(encoded_image)
    decoded_image.save(path)
    return path

@function_tool
def take_a_picture():
    """Take a picture using Photo Booth application."""
    try:
        # Launch Photo Booth
        pyautogui.hotkey("command", "space", interval=0.25)
        sleep(0.5)
        pyautogui.typewrite("Photo booth")
        sleep(0.1)
        pyautogui.press("enter")
        sleep(3)
        pyautogui.press("enter")
        sleep(3)

        # Find recent photo
        photo_dir = pathlib.Path(os.getenv("PHOTO_BOOTH_PICTURE_PATH"))
        jpg_files = glob.glob(str(photo_dir / "*.jpg"), recursive=False)
        current_time = time.time()
        
        recent_files = [
            file for file in jpg_files 
            if current_time - os.path.getctime(file) <= PHOTO_RECENT_THRESHOLD
        ]

        if not recent_files:
            raise RuntimeError("Can't find photo.")
        
        return sorted(recent_files, key=os.path.getctime, reverse=True)[0]
        
    except Exception as e:
        raise RuntimeError(f"Failed to take a photo. Error: {e}")

@function_tool
def call_diffusion_model(prompt: str, image_path: str):
    """
    Call diffusion model to edit image.
    
    Args:
        prompt (str): Key descriptive terms for diffusion model, enhanced with relevant artistic keywords.
            Example: "Make this picture a cute sticker" → "cute, sticker, cel-shaded, outlined, vibrant colors"
        image_path (str): Path to image to be processed
    """
    try:
        url = os.getenv("DIFFUSION_MODEL_URL")
        base, ext = os.path.splitext(image_path)
        new_path = f"{base}_noised{ext}"

        with open(image_path, "rb") as img:
            base64_str = base64.b64encode(img.read()).decode()

        payload = {
            "prompt": prompt,
            "negative_prompt": "nsfw",
            "guidance_scale": 15,
            "image_b64": base64_str
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()

        new_image = Image.open(io.BytesIO(response.content))
        new_image.save(new_path, format="JPEG")

        return new_path
    except Exception as e:
        raise RuntimeError(f"Failed to call diffusion model. Error: {e}")

@function_tool
def send_mail(name: str, subject: str, to: str, image_path: str):
    """
    Send mail with image attachment.
    
    Args:
        name (str): Recipient's name
        subject (str): Email subject
        to (str): Recipient's email
        image_path (str): Path to image attachment
    """
    try:
        creds = GmailService.get_credentials()
        service = build("gmail", "v1", credentials=creds)
        
        # Prepare email
        mime_message = EmailMessage()
        mime_message.set_content(EMAIL_TEMPLATE)
        
        mime_message["From"] = "hyperpocket@vessl.ai"
        mime_message["To"] = to
        mime_message["Subject"] = f"[Hyperpocket] {subject}"

        # Attach image
        type_subtype, _ = mimetypes.guess_type(image_path)
        maintype, subtype = type_subtype.split("/")

        with open(image_path, "rb") as fp:
            mime_message.add_attachment(
                fp.read(), 
                maintype=maintype, 
                subtype=subtype, 
                filename="pictures.jpg"
            )

        # Send email
        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        message = service.users().messages().send(
            userId="me",
            body={"raw": encoded_message}
        ).execute()

        print(f'Message Id: {message["id"]}')
        return message
        
    except Exception as e:
        raise RuntimeError(f"Failed to send email. Error: {e}")

@function_tool(auth_provider=AuthProvider.SLACK)
def get_slack_messages(channel_id: str, limit: int = 10) -> str:
    """
    Get recent messages from a Slack channel.

    Args:
        channel_id (str): The ID of the Slack channel to fetch messages from
        limit (int): Maximum number of messages to retrieve (default: 10)
    """
    try:
        response = slack_client.conversations_history(
            channel=channel_id,
            limit=limit
        )
        
        if not response["ok"]:
            raise RuntimeError(f"Failed to get messages: {response['error']}")
            
        messages = response.get("messages", [])
        if not messages:
            return "No messages found in the channel."
            
        return SlackTools.format_messages(messages)
        
    except SlackApiError as e:
        raise RuntimeError(f"Failed to get Slack messages. Error: {str(e)}")

@function_tool(auth_provider=AuthProvider.SLACK)
def post_slack_message(
    channel_id: str,
    message: str,
    thread_ts: str = None
) -> str:
    """
    Post a message to a Slack channel.

    Args:
        channel_id (str): The ID of the Slack channel to post to
        message (str): The message text to post
        thread_ts (str, optional): Thread timestamp to reply to a thread
    """
    try:
        kwargs = {
            "channel": channel_id,
            "text": message
        }
        
        if thread_ts:
            kwargs["thread_ts"] = thread_ts
            
        response = slack_client.chat_postMessage(**kwargs)
        
        if not response["ok"]:
            raise RuntimeError(f"Failed to post message: {response['error']}")
            
        return f"Message posted successfully. Timestamp: {response['ts']}"
        
    except SlackApiError as e:
        raise RuntimeError(f"Failed to post Slack message. Error: {str(e)}")