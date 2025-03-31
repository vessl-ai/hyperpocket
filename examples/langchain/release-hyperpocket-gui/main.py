from time import sleep
from typing import Tuple
import base64
import boto3
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
import requests
from hyperpocket.config import secret
from hyperpocket.tool import from_git, function_tool, from_func
from hyperpocket.auth import AuthProvider
from hyperpocket_langchain import PocketLangchain
import pyautogui
import traceback
import os
from github import Github, Auth
from PIL import Image

from pydantic import BaseModel
from pyscreeze import Box, screenshot


@function_tool()
def move_mouse(x: int, y: int, **kwargs):
    """
    Move mouse to the given position

    Args:
    x: x coordinate
    y: y coordinate
    """
    pyautogui.moveTo(x, y, duration=1)

    return "Mouse moved to ({}, {})".format(x, y)


@function_tool()
def click_mouse():
    """
    Click mouse
    """
    sleep(0.1)
    pyautogui.click()
    sleep(0.1)

    return "Mouse clicked"


@function_tool()
def clear_input():
    """
    Clear input
    """
    pyautogui.hotkey("command", "a", interval=0.25)
    sleep(0.5)
    pyautogui.press("delete")

    return "Input cleared"


@function_tool()
def drag_mouse(x: int, y: int):
    """
    Drag mouse to the given position

    Args:
    x: x coordinate
    y: y coordinate
    """
    pyautogui.dragTo(x, y)

    return "Mouse dragged to ({}, {})".format(x, y)


@function_tool()
def input_keyboard_key(keyname: str):
    """
    input keyboard key

    Args:
      keyname: lowercase key name
    """
    pyautogui.keyDown(keyname)
    pyautogui.keyUp(keyname)

    return "keyname typed"


@function_tool()
def type_word(word: str):
    """
    type word
    """
    pyautogui.typewrite(word)

    return "word typed"


@function_tool()
def open_browser():
    """
    Open browser
    """
    print("Opening browser")
    print("[RUN] CMD + SPACE")
    pyautogui.hotkey("command", "space", interval=0.25)
    sleep(1)

    print("[RUN] type chrome")
    pyautogui.typewrite("chrome")
    sleep(1)

    print("[RUN] ENTER")
    pyautogui.press("enter")
    sleep(1)

    print("[RUN] CMD + T")
    pyautogui.hotkey("command", "t", interval=0.25)

    return "Browser opened"


@function_tool()
def focus_browser():
    """
    Focus browser
    """
    print("Focusing browser")
    print("[RUN] CMD + SPACE")
    pyautogui.hotkey("command", "space", interval=0.25)
    sleep(1)

    print("[RUN] type chrome")
    pyautogui.typewrite("chrome")
    sleep(1)

    print("[RUN] ENTER")
    pyautogui.press("enter")
    sleep(1)

    return "Browser focused"


@function_tool()
def enter_url(url: str):
    """
    Enter url
    """
    pyautogui.typewrite(url)
    pyautogui.press("enter")

    return "Url entered"


@function_tool(auth_provider=AuthProvider.GITHUB)
def list_github_action_workflows(user: str, repo: str, **kwargs):
    """
    List all the github action workflows in the given repository

    Args:

    user: github user name
    repo: github repository name
    """
    token = kwargs["GITHUB_TOKEN"]

    res = requests.get(
        f"https://api.github.com/repos/{user}/{repo}/actions/workflows",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )

    return res.json()


@function_tool()
def generate_url_for_github_workflow(
    user: str, repo: str, workflow_yaml_file_name: str, **kwargs
):
    """
    Generate url for the github workflow

    Args:

    user: github user name
    repo: github repository name
    workflow_yaml_file_name: workflow yaml file name
    """
    url = (
        f"https://github.com/{user}/{repo}/actions/workflows/{workflow_yaml_file_name}"
    )

    return url


def process_position(screenshotImage: Image, pos: pyautogui.Point):
    screensize = pyautogui.size()
    ratioX = screensize.width / screenshotImage.width
    ratioY = screensize.height / screenshotImage.height
    return pos.x * ratioX, pos.y * ratioY


@function_tool()
def locate_button_start_run_workflow(confidence: float = 0.9):
    """
    Locate start run workflow button

    Args:
    confidence (float): confidence level for image recognition, 0 to 1
    """
    try:
        # button_location = pyautogui.locateCenterOnScreen(
        #     "images/button-start-run-workflow.png",
        #     confidence=confidence,
        # )
        screenshot = pyautogui.screenshot()
        # screenshot.save("screenshot-start.png")
        button_box = pyautogui.locate(
            "images/button-start-run-workflow.png", screenshot, confidence=confidence
        )
        button_location = process_position(screenshot, pyautogui.center(button_box))
    except Exception as e:
        traceback.print_exc()
        return f"Button not found : {e}"

    return {"x": button_location[0], "y": button_location[1]}


@function_tool()
def locate_input_version_to_publish(confidence: float = 0.9):
    """
    Locate input version to publish

    Args:
    confidence (float): confidence level for image recognition, 0 to 1
    """
    try:
        # button_location = pyautogui.locateCenterOnScreen(
        #     "images/input-version-to-publish.png",
        #     confidence=confidence,
        # )
        screenshot = pyautogui.screenshot()
        # screenshot.save("screenshot-input.png")
        button_box = pyautogui.locate(
            "images/input-version-to-publish.png", screenshot, confidence=confidence
        )
        button_location = process_position(screenshot, pyautogui.center(button_box))
    except Exception as e:
        # traceback.print_exc()
        return f"Input version handle not found on screen : {e}"

    return {"x": button_location[0], "y": button_location[1]}


@function_tool()
def locate_button_submit_run_workflow(confidence: float = 0.9):
    """
    Locate submit run workflow button

    Args:
    confidence (float): confidence level for image recognition, 0 to 1
    """
    try:
        # button_location = pyautogui.locateCenterOnScreen(
        #     "images/button-start-run-workflow.png",
        #     confidence=confidence,
        # )
        screenshot = pyautogui.screenshot()
        # screenshot.save("screenshot-submit.png")
        button_box = pyautogui.locate(
            "images/button-submit-run-workflow.png", screenshot, confidence=confidence
        )
        button_location = process_position(screenshot, pyautogui.center(button_box))
    except Exception as e:
        traceback.print_exc()
        return f"Button not found : {e}"

    return {"x": button_location[0], "y": button_location[1]}


def get_screenshot_base64():
    """
    Get screenshot from the screen and return base64 encoded image
    """
    img = pyautogui.screenshot()
    img_base64 = base64.b64encode(img.tobytes()).decode("utf-8")

    return img_base64


def get_screenshot():
    """
    Get screenshot from the screen, upload it to the server and return the url
    """
    img = pyautogui.screenshot()

    # upload to s3 using boto3
    try:
        s3 = boto3.client("s3")
        bucket_name = "hyperpocket-test"
        key = "screenshot.png"
        img.save("screenshot.png")
        s3.upload_file("screenshot.png", bucket_name, key)
        url = s3.generate_presigned_url(
            "get_object", Params={"Bucket": bucket_name, "Key": key}, ExpiresIn=3600
        )
        # url = f"https://{bucket_name}.s3.ap-northeast-2.amazonaws.com/{key}"

        return url
    except Exception as e:
        traceback.print_exc()
        return None


def postprocess_screenshot_url(x):
    if x is None:
        return None
    return {
        "type": "image_url",
        "image_url": {"url": f"{x}"},
    }


def postprocess_screenshot_base64(x):
    if x is None:
        return None
    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/png;base64,{x}"},
    }


def agent():
    pocket = PocketLangchain(
        tools=[
            move_mouse,
            click_mouse,
            drag_mouse,
            input_keyboard_key,
            clear_input,
            type_word,
            open_browser,
            focus_browser,
            enter_url,
            list_github_action_workflows,
            generate_url_for_github_workflow,
            locate_button_start_run_workflow,
            locate_input_version_to_publish,
            locate_button_submit_run_workflow,
        ]
    )
    tools = pocket.get_tools()

    llm = ChatOpenAI(model="gpt-4o", api_key=secret["OPENAI_API_KEY"])

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                #                 """
                # You are a window automation agent. You can ask me to move mouse, click mouse, input keyboard key.
                # You will be provided with a url of screenshot of the screen for your reference for every user command.
                # You have to read the screenshot from the url EVERYTIME when you are provided and determine the x and y coordinates for mouse movement for the command.
                # And you will call `move_mouse` tool with the x and y coordinates.
                # """,
                """
You are a gui automation agent focused on releasing github source by running github workflow.
For successful action, you first plan the steps and get review.
After the confirmation by the user, you will run the workflow step by step.
Utilize given tools to automate the process.

General steps:
1. List all the github action workflows
2. Open browser
3. Generate url for the github workflow
4. Go to the generated url
5. Locate the start run workflow button
6. Click the start run workflow button
7. Locate the input version to publish and clear the input
8. Input the version to publish
9. Locate the submit run workflow button
10. Refresh the page so that user can see the workflow started

When locating in screen, you should start by using higher confidence level and decrease it if not found.
""",
            ),
            ("placeholder", "{chat_history}"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
    )

    print("\n\n\n")
    print("Hello, this is test GUI control agent.")
    while True:
        print("user(q to quit) : ", end="")
        user_input = input()
        if user_input == "q":
            print("Good bye!")
            break

        response = agent_executor.invoke({"input": user_input})
        print("agent : ", response["output"])
        print()


if __name__ == "__main__":
    agent()
