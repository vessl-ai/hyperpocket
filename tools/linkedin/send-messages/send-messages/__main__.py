import json
import os
import sys
from datetime import datetime, timedelta
import time
import traceback
from typing import List, Optional

from pydantic import BaseModel, Field
from playwright.sync_api import sync_playwright, TimeoutError, Page
import base64


print("Loading environment variables...")


class LinkedInSendMessagesTarget(BaseModel):
    profile_url: str
    name: str
    message: str


class LinkedInSendMessagesRequest(BaseModel):
    targets: List[LinkedInSendMessagesTarget]


class LinkedInSendMessagesResponse(BaseModel):
    result: Optional[List[str]] = None
    error: Optional[str] = None


print("Initializing OpenAI client...")
from openai import OpenAI

basic_auth = os.getenv("BASIC_AUTH")


def handle_model_action(page, action):
    """
    Given a computer action (e.g., click, double_click, scroll, etc.),
    execute the corresponding operation on the Playwright page.
    """
    action_type = action.type

    try:
        match action_type:
            case "click":
                x, y = action.x, action.y
                button = action.button
                print(f"Action: click at ({x}, {y}) with button '{button}'")
                # Not handling things like middle click, etc.
                if button != "left" and button != "right":
                    button = "left"
                page.mouse.click(x, y, button=button)

            case "scroll":
                x, y = action.x, action.y
                scroll_x, scroll_y = action.scroll_x, action.scroll_y
                print(
                    f"Action: scroll at ({x}, {y}) with offsets (scroll_x={scroll_x}, scroll_y={scroll_y})"
                )
                page.mouse.move(x, y)
                page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")

            case "keypress":
                keys = action.keys
                # check if first key is modifier
                if keys[0].lower() in ["cmd", "ctrl", "shift", "alt"]:
                    modifier = keys[0].lower()
                    if modifier == "cmd":
                        modifier = "Meta"
                    elif modifier == "ctrl":
                        modifier = "Control"
                    elif modifier == "shift":
                        modifier = "Shift"
                    elif modifier == "alt":
                        modifier = "Alt"
                    combined_keys = modifier + "+" + "+".join(keys[1:])
                    print(f"Action: keypress '{combined_keys}'")
                    page.keyboard.press(combined_keys)
                else:
                    for k in keys:
                        print(f"Action: keypress '{k}'")
                        # A simple mapping for common keys; expand as needed.
                        if k.lower() == "enter":
                            page.keyboard.press("Enter")
                        elif k.lower() == "space":
                            page.keyboard.press(" ")
                        else:
                            page.keyboard.press(k)

            case "type":
                text = action.text
                print(f"Action: type text: {text}")
                page.keyboard.type(text)

            case "wait":
                print(f"Action: wait")
                time.sleep(2)

            case "screenshot":
                # Nothing to do as screenshot is taken at each turn
                print(f"Action: screenshot")

            # Handle other actions here

            case _:
                print(f"Unrecognized action: {action}")

    except Exception as e:
        print(f"Error handling action {action}: {e}")


def cua_to_action(page: Page, instruction: str):
    # resize page to 1024x768
    page.set_viewport_size({"width": 1024, "height": 768})
    initial_screenshot = page.screenshot()
    initial_screenshot_base64 = base64.b64encode(initial_screenshot).decode("utf-8")
    system_prompt = f"""
You are a helpful assistant that can control a web browser to complete tasks on LinkedIn. Your main goal is to help the user efficiently perform actions on LinkedIn without needing additional confirmation or prompts.

You are allowed to:
1. Search for people, companies, posts, or jobs.
2. Navigate to profiles, job listings, or company pages.
3. Send connection requests to people.
4. Send direct messages to 1st-degree connections.
5. Send custom notes with connection requests when applicable.
6. Scroll, click, type, and interact with LinkedIn like a human would.

Execute all actions **autonomously**, without requiring confirmation from the user for each step. Act as if you are the user operating the browser.

Message Sending:
- If the target user is a 1st-degree connection, open the message window and send the given message.
- If not connected, send a connection request with the message as a custom note.
- Do not prompt the user to confirm message content or recipient — proceed immediately once the instruction is understood.
- Ensure fields (recipient, message body) are populated correctly before sending.

Behavior Guidelines:
- Emulate natural, human-like usage patterns (reasonable typing, scrolling, and pauses).
- Be resilient to UI changes (e.g., if a button is not visible, scroll or try alternative labels).
- Avoid excessive or repetitive actions that might trigger anti-bot detection.
- Only interact with content that is publicly visible or accessible to the currently logged-in user.
- Never attempt to bypass authentication or solve CAPTCHAs.
- Never download files or execute JavaScript.

You are currently logged into LinkedIn as the user and have full authority to act on their behalf.
"""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception as e:
        print(f"Error creating OpenAI client: {str(e)}")
        return None

    screenshot = page.screenshot()
    screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
    response = client.responses.create(
        model="computer-use-preview-2025-03-11",
        tools=[
            {
                "type": "computer_use_preview",
                "display_width": 1024,
                "display_height": 768,
                "environment": "browser",
            }
        ],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": system_prompt,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": instruction,
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{initial_screenshot_base64}",
                    },
                ],
            },
        ],
        reasoning={"generate_summary": "concise"},
        truncation="auto",
    )

    try:
        while True:
            reasoning = list(filter(lambda x: x.type == "reasoning", response.output))
            print("Reasoning: ", reasoning)
            computer_calls = [
                item for item in response.output if item.type == "computer_call"
            ]
            if not computer_calls:
                print("No computer call found. Output from model:")
                for item in response.output:
                    print(item)
                break  # Exit when no computer calls are issued.

            computer_call = computer_calls[0]
            last_call_id = computer_call.call_id
            action = computer_call.action

            handle_model_action(page, action)
            time.sleep(1)

            screenshot = page.screenshot()
            screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
            response = client.responses.create(
                model="computer-use-preview-2025-03-11",
                previous_response_id=response.id,
                tools=[
                    {
                        "type": "computer_use_preview",
                        "display_width": 1024,
                        "display_height": 768,
                        "environment": "browser",
                    }
                ],
                input=[
                    {
                        "call_id": last_call_id,
                        "type": "computer_call_output",
                        "output": {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{screenshot_base64}",
                        },
                    }
                ],
                truncation="auto",
            )
        return {
            "success": True,
            "message": f"Successfully completed task: {instruction}",
        }
    except Exception as e:
        message = f"Error doing task: {str(e)}, instruction: {instruction}"
        print(message)
        traceback.print_exc()
        return {"success": False, "message": message}


def send_with_browser_control(page: Page, name: str, message: str):
    """
    Control the browser to complete the task.
    """

    try:
        print("Waiting for message button...")
        # select send message button
        page.wait_for_timeout(10000)  # just wait
        send_message_button = page.query_selector_all('button[aria-label^="Message"]')[
            1
        ]  # second one
        send_message_button.click()
        print("Message button clicked")

        print("Waiting for message textbox...")
        page.wait_for_selector('div[role="textbox"]', timeout=10000)

        # select message input
        message_input = page.locator('div[role="textbox"]')
        message_input.click()
        print("Typing message...")
        page.keyboard.type(message, delay=100)
        print("Message typed")

        # select send button
        # Wait for send button to be enabled
        print("Waiting for send button...")
        page.wait_for_selector('button[type="submit"]:not([disabled])', timeout=10000)
        send_button = page.locator('button[type="submit"]:not([disabled])')
        send_button.click()
        print("Message sent")

        return {"success": True, "message": f"Message sent successfully to {name}"}
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        traceback.print_exc()
        return {"success": False, "message": str(e)}


def send_messages(
    req: LinkedInSendMessagesRequest,
) -> LinkedInSendMessagesResponse:
    print(f"Starting LinkedIn message send")
    with sync_playwright() as p:
        print("Launching browser")
        browser = p.chromium.launch(
            headless=False, args=["--disable-extentions", "--disable-file-system"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_viewport_size({"width": 1024, "height": 768})
        print("Navigating to LinkedIn")
        import base64

        [email, password] = base64.b64decode(basic_auth).decode().split(":")

        try:
            print("Attempting to login to LinkedIn...")
            # Login to LinkedIn
            page.goto("https://www.linkedin.com/login")
            page.type("#username", email, delay=100)
            page.type("#password", password, delay=100)
            page.click("button[type='submit']")

            # Wait for login to complete
            print("Waiting for login completion...")
            try:
                # Wait for feed page and its main content
                page.wait_for_url("https://www.linkedin.com/feed/", timeout=5000)
                page.wait_for_selector("div.feed-outlet", timeout=10000)
                print("Successfully logged in to LinkedIn")
            except TimeoutError:
                if page.url.startswith(
                    "https://www.linkedin.com/checkpoint/challenge/"
                ):
                    print("Login challenge detected")
                    return LinkedInSendMessagesResponse(
                        result=None,
                        error=f"Failed to login at url {page.url}",
                    )
                    # disable for now
                    print("Solving challenge...")
                    result = cua_to_action(page)
                    if result != "Success":
                        print("Failed to solve challenge")
                        print("Login failed - taking screenshot for debugging")
                        # Take screenshot if not redirected to feed
                        return LinkedInSendMessagesResponse(
                            result=None,
                            error="Failed to login",
                            # screenshot=screenshot_base64,
                        )

                    # retry waiting for feed page
                    page.wait_for_url("https://www.linkedin.com/feed/", timeout=15000)
                    page.wait_for_selector("div.feed-outlet", timeout=10000)
                    print("Successfully logged in to LinkedIn")
                else:
                    print("Login failed")
                    url = page.url
                    # Take screenshot if not redirected to feed
                    return LinkedInSendMessagesResponse(
                        result=None,
                        error=f"Failed to login at url {url}",
                    )

            results = []
            for target in req.targets:
                print(f"Navigating to user profile page {target.profile_url}...")
                page.goto(target.profile_url)
                # result = cua_to_action(
                #     page,
                #     f"Send a message to {target.name} with the following message: {target.message}",
                # )
                result = send_with_browser_control(
                    page,
                    target.name,
                    target.message,
                )
                if not result["success"]:
                    print("Failed to send message")
                    return LinkedInSendMessagesResponse(
                        result=results,
                        error=f"Failed to send message to {target.name}",
                    )
                results.append(result["message"])

            return LinkedInSendMessagesResponse(
                result=results,
                error=None,
            )

        except Exception as e:
            print(f"Fatal error occurred: {str(e)}")
            return LinkedInSendMessagesResponse(
                result=None,
                error=f"Failed to send LinkedIn messages: {str(e)}",
            )
        finally:
            print("Closing browser...")
            browser.close()


def main():
    print("Starting LinkedIn message sender...")
    if not sys.stdin.isatty():
        print("Reading request from stdin...")
        req = json.load(sys.stdin.buffer)
        req_typed = LinkedInSendMessagesRequest.model_validate(req)
    else:
        print("No stdin input, using default request...")
        req_typed = LinkedInSendMessagesRequest(targets=[])
    print("Processing request...")
    response = send_messages(req_typed)
    print("Request completed, outputting response...")
    result = response.model_dump_json(indent=2)
    print(result)


if __name__ == "__main__":
    print("Starting LinkedIn connection fetcher main process...")
    main()
