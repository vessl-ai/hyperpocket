from typing import Tuple
import base64
import boto3
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from hyperpocket.config import secret
from hyperpocket.tool import from_git, function_tool, from_func
from hyperpocket_langchain import PocketLangchain
import pyautogui
import traceback
import os

from pydantic import BaseModel
from pyscreeze import Box


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
    pyautogui.click()

    return "Mouse clicked"


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
def focus_calc(**kwargs):
    """
    Focus on calculator
    """
    try:
        img_path = os.getcwd() + "/images/calc.png"
        print(img_path)
        calc_loc = pyautogui.locateOnScreen(img_path, confidence=0.9)
        point = pyautogui.center(calc_loc)
        pyautogui.moveTo(point.x, point.y, duration=1)
        pyautogui.click()

        return "Calculator focused, calculator box: (left={}, top={}, width={}, height={})".format(
            calc_loc.left, calc_loc.top, calc_loc.width, calc_loc.height
        )
    except Exception as e:
        traceback.print_exc()
        return "Calculator not found: {}".format(e)


@function_tool()
def clear_calc():
    """
    Clear calculator
    """
    pyautogui.press("esc")
    pyautogui.press("esc")
    pyautogui.press("esc")
    return "Calculator cleared"


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


class CalculatorPosition(BaseModel):
    left: int
    top: int
    width: int
    height: int


@function_tool()
def enter_calc_key(key_name: str, calculator_pos: CalculatorPosition, **kwargs):
    """
    Enter key in calculator

    Args:
    key_name: key to enter
        - 0-9: number keys
        - `.`: dot key
        - `+`: plus key
        - `-`: minus key
        - `*`: multiply key
        - `/`: divide key
        - `=`: equal key

    calculator_pos: position of calculator box, (left, top, width, height)
    """

    key_img_name = os.getcwd() + "/images/key-{}.png".format(key_name)
    if key_name == "=":
        key_img_name = os.getcwd() + "/images/key-equal.png"
    elif key_name == "+":
        key_img_name = os.getcwd() + "/images/key-plus.png"
    elif key_name == "-":
        key_img_name = os.getcwd() + "/images/key-minus.png"
    elif key_name == "*":
        key_img_name = os.getcwd() + "/images/key-multiply.png"
    elif key_name == "/":
        key_img_name = os.getcwd() + "/images/key-divide.png"
    elif key_name == ".":
        key_img_name = os.getcwd() + "/images/key-dot.png"
    elif key_name == "calc":
        key_img_name = os.getcwd() + "/images/calc.png"

    try:
        calc_image = pyautogui.screenshot(
            region=(
                calculator_pos.left,
                calculator_pos.top,
                calculator_pos.width,
                calculator_pos.height,
            )
        )
        key_loc = pyautogui.locate(key_img_name, calc_image, confidence=0.985)
        point = pyautogui.center(key_loc)

        x = calculator_pos.left + point.x
        y = calculator_pos.top + point.y
        pyautogui.moveTo(x, y, duration=1)
        pyautogui.click()

        return "Key {} entered".format(key_name)
    except Exception as e:
        traceback.print_exc()
        return "Key {} not found: {}".format(key_name, e)


def get_reference_image(key_name: str, **kwargs):
    """
    Get reference image for the given key

    Args:
    key_name: key to reference image
        - 0-9: key for calculator number
        - `.`: key for dot key
        - `+`: key for plus key
        - `-`: key for minus key
        - `*`: key for multiply key
        - `/`: key for divide key
        - `=`: key for equal key
        - calc: key for calculator
    """

    key_img_name = os.getcwd() + "/images/key-{}.png".format(key_name)
    if key_name == "=":
        key_img_name = os.getcwd() + "/images/key-equal.png"
    elif key_name == "+":
        key_img_name = os.getcwd() + "/images/key-plus.png"
    elif key_name == "-":
        key_img_name = os.getcwd() + "/images/key-minus.png"
    elif key_name == "*":
        key_img_name = os.getcwd() + "/images/key-multiply.png"
    elif key_name == "/":
        key_img_name = os.getcwd() + "/images/key-divide.png"
    elif key_name == ".":
        key_img_name = os.getcwd() + "/images/key-dot.png"

    img_base64 = None
    with open(key_img_name, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    return img_base64


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
            # from_func(get_screenshot).with_postprocessing(postprocess_screenshot_url),
            # # from_func(get_screenshot_base64).with_postprocessing(
            # #     postprocess_screenshot_base64
            # # ),
            # from_func(get_reference_image).with_postprocessing(
            #     postprocess_screenshot_base64
            # ),
            # move_mouse,
            # click_mouse,
            # input_keyboard_key,
            focus_calc,
            clear_calc,
            enter_calc_key,
        ]
    )
    tools = pocket.get_tools()

    llm = ChatOpenAI(model="gpt-4o", api_key=secret["OPENAI_API_KEY"])

    prompt = ChatPromptTemplate.from_messages(
        [
            ("placeholder", "{chat_history}"),
            (
                "system",
                #                 """
                # You are a window automation agent. You can ask me to move mouse, click mouse, input keyboard key.
                # You will be provided with a url of screenshot of the screen for your reference for every user command.
                # You have to read the screenshot from the url EVERYTIME when you are provided and determine the x and y coordinates for mouse movement for the command.
                # And you will call `move_mouse` tool with the x and y coordinates.
                # """,
                """
You are a window automation agent.
You can focus on calculator, clear calculator, enter key in calculator.
""",
            ),
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
    print("Hello, this is langchain desktop calculator agent.")
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
