import asyncio
import inspect
import json
import os
import re
import uuid
from typing import Optional, List

import gradio as gr
import pathlib
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletion

from hyperpocket.tool.function import FunctionTool
from hyperpocket_openai import PocketOpenAI
from template.code_template import get_template
from tools import send_mail, take_a_picture, call_diffusion_model
from utils.build_javascript_tool import build_javascript_tool
from utils.build_python_tool import build_python_tool
from utils.upload_to_repo import upload_to_repo

load_dotenv()

cur_dir = pathlib.Path(os.getcwd())
email_list = cur_dir / "email_list.txt"
tools_cache_path = cur_dir / ".tools_cache.json"
if not tools_cache_path.exists():
    with open(tools_cache_path, "w") as f:
        json.dump({}, f)

with open(tools_cache_path, "r") as f:
    try:
        tools = json.load(f)
    except Exception as e:
        print("failed to load tools cache")
        tools = {}

tools |= {
    send_mail.name: {"tool": send_mail},
    take_a_picture.name: {"tool": take_a_picture},
    call_diffusion_model.name: {"tool": call_diffusion_model},
}

MODEL_NAME = "gpt-4o"
pocket: Optional[PocketOpenAI] = None
llm: Optional[OpenAI] = None
tool_specs: List[dict] = []

messages = [{
    "role": "system",
    "content": """You are a photo-taking agent. you can take pictures of users and transform their photos into sticker-style images.
If users want to receive their original or sticker photos, you can send them an email with the images.

All users should follow below step one by one and they can't skip any step.
at the first time, you introduce yourself to a user and the processes. 

1. take a photo by using the "take_a_picture" tool.
  - you don't need to return the saved path of the picture. simply inform the user whether the photo was taken successfully or not.
  - after taking a photo, ask the user if they want to transform their photos into sticker-style images. 
2. ask for concrete style of the sticker and do transform by using the "call_diffusion_model" tool.
  - after transforming the photo, ask the user if they are satisfied with the result. if they say yes, ask if they would like the photo sent to their email.
3. ask for their email address and send the photo accordingly.
4. After doing all this processes, next user will be coming soon. so don't confuse previous user and next user. 
"""
}]
history = []


def add_tool(tool_name, tool_path, code):
    tools[str(tool_name)] = {"tool": str(tool_path), "code": code}
    with open(tools_cache_path, "w") as f:
        str_tools = {name: tool for name, tool in tools.items() if isinstance(tool["tool"], str)}
        json.dump(str_tools, f)


def delete_tool(tool_path):
    target_name = None
    for name, tool in tools.items():
        if isinstance(tool["tool"], str) and tool_path == tool["tool"]:
            target_name = name
            break

    if target_name:
        del tools[target_name]
        with open(tools_cache_path, "w") as f:
            str_tools = {name: tool for name, tool in tools.items() if isinstance(tool["tool"], str)}
            json.dump(str_tools, f)
    return


def build_chat_ui(state):
    def append_user_message(message):
        user_message = {"role": "user", "content": message}
        messages.append(user_message)
        history.append(gr.ChatMessage(role="user", content=user_message["content"]))
        return gr.update(value=history), gr.update(interactive=False)

    async def _chat(current_picture_path,
                    is_picture_refresh_needed):  # user message is already appended in `append_user_message`
        is_picture_refresh_needed = False
        while True:
            response: ChatCompletion = llm.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tool_specs,
            )
            choice = response.choices[0]
            messages.append(choice.message)
            if choice.finish_reason == "stop":
                break

            elif choice.finish_reason == "tool_calls":
                tool_calls: List[ChatCompletionMessageToolCall] = choice.message.tool_calls
                for tool_call in tool_calls:
                    tool_message = await pocket.ainvoke(tool_call)

                    if not "failed to" in tool_message["content"]:
                        if tool_call.function.name == "take_a_picture" or tool_call.function.name == "call_diffusion_model":
                            current_picture_path = tool_message["content"]
                            is_picture_refresh_needed = True
                        elif tool_call.function.name == "send_mail":
                            with open(email_list, "a") as f:
                                f.write(f"{tool_call.function.arguments}\n")

                    messages.append(tool_message)

        history.append(gr.ChatMessage(role="assistant", content=messages[-1].content))
        return gr.update(value=history), current_picture_path, is_picture_refresh_needed, gr.update(value=None,
                                                                                                    interactive=True)

    def _update_image(path: str, refresh: bool):
        if not refresh:
            return gr.update(), False

        if path is None:
            return gr.update(value=None, visible=False), False

        return gr.update(value=path, visible=True, elem_id=str(uuid.uuid4())), False

    with gr.Blocks() as ui:
        image = gr.Image(height=400, width=600, visible=False)

        chat_bot = gr.Chatbot(type="messages")
        text = gr.Text(submit_btn=True, lines=1, show_label=False)

        with gr.Blocks():
            log_output = gr.Textbox(label="Log", lines=20, interactive=False)

        text.submit(
            fn=append_user_message,
            inputs=[text],
            outputs=[chat_bot, text],
        ).then(
            fn=_chat,
            inputs=[state["current_picture_path"], state["is_picture_refresh_needed"]],
            outputs=[chat_bot, state["current_picture_path"], state["is_picture_refresh_needed"], text]
        )

        ui.load(
            _update_image,
            inputs=[state["current_picture_path"], state["is_picture_refresh_needed"]],
            outputs=[image, state["is_picture_refresh_needed"]]
        )
        ui.load(
            lambda: gr.update(value=history),
            outputs=[chat_bot]
        )

        def _stream_logs():
            global log_offset, log_history
            pattern = r'(\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]) .*?(\[pocket_logger\])'

            with open(log_path, "r") as f:
                f.seek(log_offset)
                new_lines = [re.sub(pattern, r'\1 \2', line) for line in f.readlines()]
                log_history = list(reversed(new_lines)) + log_history
                log_offset = f.tell()

            log = "".join(log_history)
            return gr.update(value=log, elem_id=str(uuid.uuid4()))

        ui.load(
            _stream_logs,
            inputs=None,
            outputs=[log_output]
        )

        timer = gr.Timer(value=1)
        timer.tick(
            _stream_logs,
            inputs=None,
            outputs=[log_output]
        )

        state["is_picture_refresh_needed"].change(
            _update_image,
            inputs=[state["current_picture_path"], state["is_picture_refresh_needed"]],
            outputs=[image, state["is_picture_refresh_needed"]],
        )


def build_tool_list_ui(state):
    PREBUILT_TOOL_LIST_NUMBER = 100
    AUTH_PROVIDERS = [None, "google", "slack", "github"]
    AUTH_HANDLERS = {
        None: [],
        "google": ["google-oauth2"],
        "slack": ["slack-oauth2", "slack-token"],
        "github": ["github-oauth2", "github-token"],
    }

    def _upload(
            name: str, language: str, code: str, auth_provider: str = None, auth_handler: str = None, scopes=None,
            dependencies: str = None, upload_to_github: bool = False, *args, **kwargs):
        def _name_is_valid(_name):
            return not bool(re.search(r'[^a-zA-Z_]', _name)) and _name is not None and _name != ""

        if not _name_is_valid(name):
            raise gr.Error(
                message="Name isn't valid. shouldn't be empty and shouldn't include other characters except for (a-zA-Z_)",
                duration=3)

        if dependencies == "":
            dependencies = None
        elif dependencies is not None:
            dependencies = dependencies.split("\n")

        base_path = pathlib.Path(f"./tools/").resolve()
        if not base_path.exists():
            base_path.mkdir()

        tool_name = f"{name}_get_user_email"
        tool_path = base_path / tool_name
        tool_description = f"get {name}'s email to send sticker photo to the user."

        try:
            if language == "python":
                build_python_tool(
                    base_path=base_path,
                    tool_name=tool_name,
                    tool_description=tool_description,
                    language=language,
                    code=code,
                    auth_provider=auth_provider,
                    auth_handler=auth_handler,
                    scopes=scopes,
                    dependencies=dependencies
                )
            elif language == "javascript":
                build_javascript_tool(
                    base_path=base_path,
                    tool_name=tool_name,
                    tool_description=tool_description,
                    language=language,
                    code=code,
                    auth_provider=auth_provider,
                    auth_handler=auth_handler,
                    scopes=scopes,
                    dependencies=dependencies
                )
        except Exception as e:
            raise gr.Error(message=str(e), duration=10)

        if upload_to_github:
            github_repo_url = upload_to_repo(
                directory_path=tool_path,
                repo_name=tool_name,
                description=tool_description
            )

            uploaded_tool_name, uploaded_tool_path = github_repo_url, github_repo_url
        else:
            uploaded_tool_name, uploaded_tool_path = tool_name, tool_path

        add_tool(uploaded_tool_name, uploaded_tool_path, code)
        try:
            init_model()
        except Exception as e:
            init_model()
            raise gr.Error(f"failed to init model. {str(e)}", duration=5)

        return {
            "tool_name": uploaded_tool_name,
            "tool_path": uploaded_tool_path,
            "tool_description": tool_description,
            "code": code,
            "index": len(tools) - 1
        }

    def _refresh_tool_list():
        tool_detail_list = []
        tool_code_list = []
        tool_delete_button_list = []
        tool_name_list = []

        for tool_name, tool in tools.items():
            tool_name_list.append(gr.update(value=tool_name))
            if isinstance(tool["tool"], FunctionTool):
                code = inspect.getsource(tool["tool"].func)

                if tool_name == "send_mail":
                    tool_name = f"✉️\t{tool_name}"
                elif tool_name == "take_a_picture":
                    tool_name = f"📷\t{tool_name}"
                elif tool_name == "call_diffusion_model":
                    tool_name = f"🤖\t{tool_name}"

                tool_detail = gr.update(label=tool_name, visible=True)
                tool_code = gr.update(value=code)
                tool_delete_button = gr.update(interactive=False)

            elif isinstance(tool["tool"], str):
                code = tool["code"]

                tool_detail = gr.update(label=f"⚒️\t{tool_name}", visible=True)
                tool_code = gr.update(value=code)
                tool_delete_button = gr.update(interactive=True)

            else:
                tool_detail = gr.update()
                tool_code = gr.update()
                tool_delete_button = gr.update()

            tool_detail_list.append(tool_detail)
            tool_code_list.append(tool_code)
            tool_delete_button_list.append(tool_delete_button)

        for _ in range(PREBUILT_TOOL_LIST_NUMBER - len(tools)):
            tool_detail = gr.update(visible=False)
            tool_name = gr.update(visible=False)
            tool_code = gr.update()
            tool_delete_button = gr.update()

            tool_detail_list.append(tool_detail)
            tool_name_list.append(tool_detail)
            tool_code_list.append(tool_code)
            tool_delete_button_list.append(tool_delete_button)

        return *tool_detail_list, *tool_code_list, *tool_delete_button_list, *tool_name_list

    def _build_code_ui(language: str):
        return gr.Code(
            get_template(language),
            language=language,
            interactive=True,
            lines=20)

    def _build_auth_handlers(selected_provider, selected_handler):
        handler_list = AUTH_HANDLERS.get(selected_provider, [])
        return gr.update(choices=handler_list, value=handler_list[0] if len(handler_list) > 0 else None)

    def _delete_tool(tool_name: str):
        tool = tools.get(tool_name)
        if tool is None:
            print("not found tool :", tool_name)
            return gr.update(visible=False), gr.update(), gr.update()

        delete_tool(tool["tool"])
        return gr.update(visible=False), gr.update(), gr.update()

    with gr.Blocks() as tool_list_ui:
        with gr.Accordion(label="Tool list", open=False):
            with gr.Column():
                tool_detail_list = []
                tool_name_list = []
                tool_code_list = []
                tool_delete_button_list = []

                for _ in range(PREBUILT_TOOL_LIST_NUMBER):
                    with gr.Accordion(open=False, visible=False) as tool_detail:
                        tool_name = gr.Text(visible=False)
                        tool_code = gr.Code(language="python")
                        tool_delete_button = gr.Button("delete", scale=0, size="md", min_width=10)

                        tool_delete_button.click(
                            _delete_tool,
                            inputs=[tool_name],
                            outputs=[tool_detail, tool_code, tool_delete_button]
                        ).then(
                            init_model
                        )

                    tool_detail_list.append(tool_detail)
                    tool_name_list.append(tool_name)
                    tool_code_list.append(tool_code)
                    tool_delete_button_list.append(tool_delete_button)

        with gr.Column():
            selected_langauge = gr.Radio(["python", "javascript"], value="python", label="language")
            name = gr.Text(label="name", placeholder="user name")
            with gr.Accordion(label="Auth Setting(optional)", open=False):
                auth_provider_ui = gr.Dropdown(
                    choices=AUTH_PROVIDERS,
                    label="auth provider",
                    value=AUTH_PROVIDERS[0],
                )

                auth_handler_ui = gr.Dropdown(
                    choices=AUTH_HANDLERS.get(AUTH_PROVIDERS[0], []),
                    label="auth handler"
                )

                scopes = gr.Text(label="scopes", value=None)

                auth_provider_ui.change(
                    _build_auth_handlers,
                    inputs=[auth_provider_ui, auth_handler_ui],
                    outputs=[auth_handler_ui])

            with gr.Accordion(label="dependencies setting(optional)", open=False):
                dependencies_ui = gr.Textbox(label="dependencies", lines=5, interactive=True)

            code_ui = _build_code_ui(selected_langauge.value)

            with gr.Row():
                tool_register_button = gr.Button(value="Register", scale=5)
                upload_to_github = gr.Checkbox(label="upload to github", scale=1)

            tool_register_button.click(
                _upload,
                inputs=[name, selected_langauge, code_ui, auth_provider_ui, auth_handler_ui, scopes, dependencies_ui,
                        upload_to_github, state["uploaded_tool_info"]],
                outputs=[state["uploaded_tool_info"]]
            ).then(
                _refresh_tool_list,
                inputs=[],
                outputs=[*tool_detail_list, *tool_code_list, *tool_delete_button_list, *tool_name_list]
            )

            tool_list_ui.load(
                _refresh_tool_list,
                outputs=[*tool_detail_list, *tool_code_list, *tool_delete_button_list, *tool_name_list]
            )

            selected_langauge.change(
                _build_code_ui, selected_langauge, code_ui,
            )

    return tool_list_ui


def ui():
    with gr.Blocks(
            theme=gr.themes.Default(text_size=gr.themes.sizes.text_lg,
                                    spacing_size=gr.themes.sizes.spacing_lg)
    ) as ui:
        state = {
            "current_picture_path": gr.State(value=None),
            "is_picture_refresh_needed": gr.State(value=False),
            "is_tool_list_refresh_needed": gr.State(value=True),
            "uploaded_tool_info": gr.State(value={}),
        }

        with gr.Tab("chatbot"):
            gr.Markdown("# Hyperpocket: Plug & Play Tools for Agent, Fully Open Source")

            build_chat_ui(state)

        with gr.Tab("Tool list"):
            gr.Markdown("# Hyperpocket: Plug & Play Tools for Agent, Fully Open Source")

            build_tool_list_ui(state)

    ui.launch(
        allowed_paths=[os.getenv("PHOTO_BOOTH_PICTURE_PATH")],
    )


def init_model():
    global pocket, llm, tool_specs, tools

    if pocket:
        pocket._teardown_server()

    tool_list = [tool["tool"] for tool in tools.values()]
    pocket = PocketOpenAI(tools=tool_list)
    tool_specs = pocket.get_open_ai_tool_specs()
    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


if __name__ == "__main__":
    import os
    import pathlib

    log_path = pathlib.Path(os.getcwd()) / ".log/pocket.log"
    log_history = []
    log_offset = 0

    with open(log_path, "w") as f:
        f.write("")

    load_dotenv()
    init_model()
    asyncio.run(ui())
