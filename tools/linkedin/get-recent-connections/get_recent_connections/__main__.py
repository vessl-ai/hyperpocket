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


class LinkedInGetRecentConnectionsRequest(BaseModel):
    days: Optional[int] = Field(
        3, description="Number of days to look back for connections"
    )
    pages_to_load: Optional[int] = Field(5, description="Number of pages to load")


class Connection(BaseModel):
    name: str
    headline: Optional[str] = None
    company: Optional[str] = None
    education: Optional[str] = None
    profile_url: Optional[str] = None
    links: Optional[List[str]] = None
    experience: Optional[List[List[str]]] = None
    raw_text: Optional[str] = None
    connected_date: Optional[str] = None


class LinkedInGetRecentConnectionsResponse(BaseModel):
    connections: List[Connection] = []
    reasoning: Optional[str] = None
    error: Optional[str] = None
    screenshot: Optional[str] = None


print("Initializing OpenAI client...")
from openai import OpenAI

basic_auth = os.getenv("LINKEDIN_BASIC_AUTH")


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


def cua_to_solve_challenge(page: Page):
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
                        "text": """
System Instruction
You are an intelligent autonomous agent tasked with solving LinkedIn’s image-orientation CAPTCHA challenge, specifically identifying the image where the frog is positioned upright.

Step-by-step procedure:
	1.	Analyze all provided images quickly, using visual recognition tools to identify the frog in each.
	2.	Assess the orientation of each frog image to detect which one is correctly positioned (upright).
	•	The upright frog typically has the eyes above, legs positioned below, and natural gravity-aligned posture.
	3.	Confirm your choice by cross-verifying anatomical features such as eye placement, limb position, and overall body alignment.
	4.	Select the correctly oriented (upright) frog image swiftly and accurately.

Always aim for precision on the first attempt to mimic natural human interaction effectively.
""",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "process this verify human challenge",
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{screenshot_base64}",
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
        return "Success"
    except Exception as e:
        print(f"Error solving challenge: {str(e)}")
        traceback.print_exc()
        return None


def get_recent_connections(
    req: LinkedInGetRecentConnectionsRequest,
) -> LinkedInGetRecentConnectionsResponse:
    print(f"Starting LinkedIn connection fetch for past {req.days} days")
    with sync_playwright() as p:
        print("Launching browser")
        browser = p.chromium.launch(
            headless=True, args=["--disable-extentions", "--disable-file-system"]
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
                    return LinkedInGetRecentConnectionsResponse(
                        connections=[],
                        reasoning="Failed to login - login challenge detected",
                        error=f"Failed to login at url {page.url}",
                    )
                    # disable for now
                    print("Solving challenge...")
                    result = cua_to_solve_challenge(page)
                    if result != "Success":
                        print("Failed to solve challenge")
                        print("Login failed - taking screenshot for debugging")
                        # Take screenshot if not redirected to feed
                        return LinkedInGetRecentConnectionsResponse(
                            connections=[],
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
                    return LinkedInGetRecentConnectionsResponse(
                        connections=[],
                        reasoning="Failed to login",
                        error=f"Failed to login at url {url}",
                    )

            print("Navigating to connections page...")
            # Navigate to connections page
            page.goto("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            # Wait for connections list to load
            page.wait_for_selector(
                "div[data-view-name='connections-list']", timeout=10000
            )
            print("Successfully loaded connections page")

            # scroll to bottom of page
            def scroll_down():
                page.evaluate(
                    "document.querySelector('main').scrollTop = document.querySelector('main').scrollHeight"
                )
                page.wait_for_timeout(1000)

            def scroll_top():
                page.evaluate("document.querySelector('main').scrollTop = 0")
                page.wait_for_timeout(1000)

            for _ in range(req.pages_to_load):  # adjustable
                scroll_down()
            scroll_top()

            # Calculate date threshold
            threshold_date = datetime.now() - timedelta(days=req.days)
            print(
                f"Looking for connections after {threshold_date.strftime('%Y-%m-%d')}"
            )

            connections = []

            print("Fetching connection elements...")
            # # connection list
            # connection_list_elem = page.query_selector(
            #     "div[data-view-name='connections-list']"
            # )

            connection_elements = page.query_selector_all(
                "a[data-view-name='connections-profile']"
            )
            # get odd index elements
            connection_elements = connection_elements[1::2]
            print(f"Found {len(connection_elements)} connection elements")

            profile_urls = [elem.get_attribute("href") for elem in connection_elements]
            print(f"Extracted {len(profile_urls)} profile URLs")

            # get the connected date
            print("Extracting connection dates...")
            connected_date_raw = [
                elem.evaluate("el => el.parentElement.lastChild.textContent")
                for elem in connection_elements
            ]

            # process with regex
            import re

            connected_date = [
                datetime.strptime(
                    re.search(r"connected on (\w+ \d{1,2}, \d{4})", text).group(1),
                    "%B %d, %Y",
                )
                for text in connected_date_raw
            ]
            print(f"Successfully parsed {len(connected_date)} connection dates")

            #             def get_profile_info_by_llm(profile_url: str, connected_date: datetime):
            #                 print(f"Processing profile: {profile_url}")

            #                 client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            #                 new_page = context.new_page()
            #                 new_page.set_viewport_size({"width": 1024, "height": 768})
            #                 new_page.goto(profile_url)
            #                 # Wait for profile main content to load
            #                 # new_page.wait_for_selector(
            #                 #     "a[href^='https://www.linkedin.com/company/']:not([href^='https://www.linkedin.com/company/setup']) > span",
            #                 #     timeout=10000,
            #                 # )
            #                 new_page.wait_for_timeout(5000)

            #                 profile_cards = new_page.query_selector("main")

            #                 # Capture profile cards section as image
            #                 if profile_cards:
            #                     print("Taking profile screenshot...")
            #                     profile_card_image = new_page.screenshot(
            #                         # path=f"profile_{re.search(r'/in/([^/]+)/', profile_url).group(1)}.png"
            #                     )

            #                 # Send profile image to OpenAI for analysis

            #                 # Convert screenshot bytes to base64
            #                 img_base64 = base64.b64encode(profile_card_image).decode("utf-8")

            #                 # Create base64 data URL for the image
            #                 data_url = f"data:image/png;base64,{img_base64}"

            #                 print("Sending profile to OpenAI for analysis...")
            #                 # Make request to OpenAI API
            #                 response = client.chat.completions.create(
            #                     model="gpt-4o",
            #                     messages=[
            #                         {
            #                             "role": "user",
            #                             "content": [
            #                                 {
            #                                     "type": "text",
            #                                     "text": f"""
            # ONLY RETURN JSON, NO MARKDOWN FORMATTING.
            # Please analyze this LinkedIn profile screenshot and extract the following information:
            # full name, current job title, current company, education history, any links to other websites.
            # Return the data in JSON format of the following schema:
            # {Connection.model_json_schema()}
            #                                     """,
            #                                 },
            #                                 {"type": "image_url", "image_url": {"url": data_url}},
            #                             ],
            #                         }
            #                     ],
            #                     max_tokens=300,
            #                 )

            #                 print("Response from OpenAI:", response.choices[0].message.content)

            #                 # Remove markdown formatting if present
            #                 content = response.choices[0].message.content
            #                 content = content.replace("```json", "").replace("```", "").strip()
            #                 response.choices[0].message.content = content

            #                 try:
            #                     profile_data = Connection(
            #                         **json.loads(response.choices[0].message.content)
            #                     )
            #                     profile_data.profile_url = profile_url
            #                     profile_data.connected_date = connected_date.strftime("%Y-%m-%d")

            #                     new_page.close()

            #                     return profile_data
            #                 except Exception as e:
            #                     print(f"Error parsing OpenAI response: {str(e)}")
            #                     traceback.print_exc()

            #                     new_page.close()

            #                     profile_data = Connection(
            #                         name="Unknown",
            #                         headline="Unknown",
            #                         company="Unknown",
            #                         education="Unknown",
            #                         profile_url=profile_url,
            #                         raw_text=response.choices[0].message.content,
            #                         connected_date=connected_date.strftime("%Y-%m-%d"),
            #                     )
            #                     return profile_data

            def get_profile_brute(profile_url: str, connected_date: datetime):
                new_page = context.new_page()
                new_page.set_viewport_size({"width": 1024, "height": 768})
                new_page.goto(profile_url)
                new_page.wait_for_selector("main", timeout=10000)

                # wait for loading to finish
                new_page.wait_for_timeout(10000)

                name = new_page.query_selector("h1").text_content()

                # headline
                headline = new_page.evaluate("""
                    () => document.querySelector("h1").parentElement.parentElement.parentElement.parentElement.children[1].innerText
                """)

                current_company = new_page.query_selector_all(
                    'button[aria-label^="Current company"]'
                )
                if current_company:
                    current_company = current_company[0].text_content().strip()
                else:
                    current_company = None
                education = new_page.query_selector_all(
                    'button[aria-label^="Education"]'
                )
                if education:
                    education = education[0].text_content().strip()
                else:
                    education = None

                # experience
                # Get experience section
                experience = []
                experience_section = new_page.query_selector(
                    '//span[text()="Experience"]/../../../../../..'
                )
                if experience_section:
                    # Navigate to parent elements to get the full experience section
                    # Get all experience list items
                    exp_items = experience_section.query_selector_all(
                        "div > ul > li.artdeco-list__item"
                    )
                    for item in exp_items:
                        # Get all text spans within each experience item
                        exp_texts = item.query_selector_all("span[aria-hidden='true']")
                        item_texts = [text.text_content() for text in exp_texts]
                        if item_texts:
                            experience.append(item_texts)

                new_page.close()

                return Connection(
                    name=name,
                    headline=headline,
                    company=current_company,
                    education=education,
                    profile_url=profile_url,
                    connected_date=connected_date.strftime("%Y-%m-%d"),
                    experience=experience,
                )

            print("Starting to process each connection...")
            for profile_url, connected_date in zip(profile_urls, connected_date):
                # Check if connection date is before threshold date
                if connected_date < threshold_date:
                    print(
                        f"Reached connections older than {threshold_date.strftime('%Y-%m-%d')}, stopping..."
                    )
                    break

                try:
                    print(
                        f"Processing connection from {connected_date.strftime('%Y-%m-%d')}"
                    )

                    # profile_data = get_profile_info_by_llm(profile_url, connected_date)
                    profile_data = get_profile_brute(profile_url, connected_date)
                    connections.append(profile_data)

                    print(f"Successfully added connection: {profile_data}")
                except Exception as e:
                    traceback.print_exc()
                    print(f"Error processing connection: {str(e)}")
                    continue

            print(f"Completed processing {len(connections)} connections")

            return LinkedInGetRecentConnectionsResponse(
                connections=connections,
                reasoning=f"Successfully fetched {len(connections)} connections after {threshold_date}",
                error=None,
                screenshot=None,
            )

        except Exception as e:
            print(f"Fatal error occurred: {str(e)}")
            return f"Failed to get LinkedIn connections: {str(e)}"
        finally:
            print("Closing browser...")
            browser.close()


def main():
    print("Starting LinkedIn connection fetcher...")
    if not sys.stdin.isatty():
        print("Reading request from stdin...")
        req = json.load(sys.stdin.buffer)
        req_typed = LinkedInGetRecentConnectionsRequest.model_validate(req)
    else:
        print("No stdin input, using default request...")
        req_typed = LinkedInGetRecentConnectionsRequest()
    print("Processing request...")
    response = get_recent_connections(req_typed)
    print("Request completed, outputting response...")
    result = response.model_dump_json(indent=2)
    print(result)


if __name__ == "__main__":
    print("Starting LinkedIn connection fetcher main process...")
    main()
