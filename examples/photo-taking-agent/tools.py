import base64
import glob
import io
import mimetypes
import os
import os.path
import pathlib
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
from googleapiclient.errors import HttpError

from hyperpocket.tool import function_tool


@function_tool
def get_encoded_image_from_path(path: str) -> str:
    """
    Get Base64 encoded string of image from path.

    Args:
        path(str): image path
    """
    with open(path, "rb") as img:
        base64_encoded_string = base64.b85encode(img.read())
    return str(base64_encoded_string)


@function_tool
def save_base64_encoded_image(path: str, encoded_image: str):
    """
    Save base64 encoded image to path.

    Args:
        path(str): path that image will be saved.
        encoded_image(str): base64 encoded image.
    """
    byte_image = literal_eval(encoded_image)
    decoded = base64.b85decode(byte_image)
    decoded_image = Image.open(io.BytesIO(decoded))
    decoded_image.save(path)
    return path


@function_tool
def take_a_picture():
    """
    take a picture
    """
    pyautogui.hotkey("command", "space", interval=0.25)
    sleep(0.5)
    pyautogui.typewrite("Photo booth")
    sleep(0.1)
    pyautogui.press("enter")
    sleep(3)
    pyautogui.press("enter")
    sleep(3)

    photo_dir = pathlib.Path(os.getenv("PHOTO_BOOTH_PICTURE_PATH"))
    jpg_files = glob.glob(str(photo_dir / "*.jpg"), recursive=False)

    if len(jpg_files) == 0:
        return

    recent_jpg_path = sorted(jpg_files, key=os.path.getmtime, reverse=True)[0]
    return recent_jpg_path


@function_tool
def call_diffusion_model(
        prompt: str,
        image_path: str,
):
    """
    call diffusion model to edit image located in image_path

    Args:
        prompt (str): Key descriptive terms for a diffusion model, enhanced with relevant artistic keywords.
              Extracted from user input while ensuring clarity and conciseness.
              Example: "Make this picture a cute sticker" → "cute, sticker, cel-shaded, outlined, vibrant colors".
        image_path (str): path to image to be sent to diffusion model.
    """
    URL = os.getenv("DIFFUSION_MODEL_URL")
    base, ext = os.path.splitext(image_path)
    new_path = f"{base}_noised{ext}"

    with open(image_path, "rb") as img:
        base64_encoded_string = base64.b64encode(img.read())

    payload = {
        "prompt": prompt,
        "negative_prompt": "nsfw",
        "guidance_scale": 15,
        "image_b64": str(base64_encoded_string)[1:-1]
    }

    # POST 요청 보내기
    response = requests.post(URL, json=payload)

    response.raise_for_status()

    new_image = Image.open(io.BytesIO(response.content))
    new_image.save(new_path, format="JPEG")

    return new_path


@function_tool
def send_mail(
        subject: str,
        to: str,
        image_path: str,
):
    """
    send mail with image.

    Args:
         subject (str): subject of email.
         to (str): recipient of email.
         image_path (str): path to image to be attached to email.
    """
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

    try:
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        service = build("gmail", "v1", credentials=creds)
        mime_message = EmailMessage()

        mime_message["From"] = "hyperpocket@vessl.ai"
        mime_message["To"] = to
        mime_message["Subject"] = subject

        mime_message.set_content("hyperpocket")

        # guessing the MIME type
        type_subtype, _ = mimetypes.guess_type(image_path)
        maintype, subtype = type_subtype.split("/")

        with open(image_path, "rb") as fp:
            attachment_data = fp.read()
        mime_message.add_attachment(attachment_data, maintype, subtype, filename="pictures.jpg")

        encoded_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )

        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message
