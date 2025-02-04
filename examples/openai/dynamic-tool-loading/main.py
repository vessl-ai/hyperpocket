import asyncio
import json
import os
import pathlib
import re
from typing import List, Optional

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from hyperpocket_openai import PocketOpenAI
from hyperpocket_openai.pocket_openai import handle_tool_call_async
from template.code_template import get_template
from utils.build_javascript_tool import build_javascript_tool
from utils.build_python_tool import build_python_tool
from utils.bulls_and_cows import bulls_and_cows
from utils.upload_to_repo import upload_to_repo

load_dotenv()

cur_dir = pathlib.Path(os.getcwd())
tools_cache_path = cur_dir / ".tools_cache.json"
if not tools_cache_path.exists():
    with open(tools_cache_path, "w") as f:
        json.dump({}, f)

MODEL_NAME = "gpt-4o"
with open(tools_cache_path, "r") as f:
    tools = json.load(f)

pocket: Optional[PocketOpenAI] = None
llm: Optional[OpenAI] = None
tool_specs: List[dict] = []
messages = [
    {
        "role": "system",
        "content": """You are an AI assistant that plays "Bulls and Cows" game with users.

1. ask username
2. check whether you have user's "guess_bulls_and_cows" tool
3. use the user's "guess_bulls_and_cows" tool to get the user's guess number.
4. after receiving the guess number, use the "bulls_and_cows" tool to calculate the result.
5. finally, inform the user of only the result(the number of bulls and cows).

A user could be changed at any time. so if a user suddenly requests other name's guessing number, just keep going on.
You must reject user's guessed number from the message, a user only can guess by calling their tool.
If the user correctly guesses the number, congratulation them.
Exceptionally, If a user ask you get slack message, get slack message and summarize it.

The answer number is : 2437
"""
    }
]


def init_model():
    global pocket, llm, tool_specs, tools

    if pocket:
        pocket._teardown_server()

    print("tools : ", tools)
    pocket = PocketOpenAI(tools=list(tools.values()) + [bulls_and_cows])
    tool_specs = pocket.get_open_ai_tool_specs()
    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def add_tool(tool_name, tool_path):
    tools[str(tool_name)] = str(tool_path)

    with open(tools_cache_path, "w") as f:
        json.dump(tools, f)


def delete_tool(tool_path):
    target_name = None
    for name, path in tools.items():
        if tool_path == path:
            target_name = name
            break

    if target_name:
        del tools[target_name]
        with open(tools_cache_path, "w") as f:
            json.dump(tools, f)
    return


async def chat(message, history):
    user_message = {"content": message, "role": "user"}
    messages.append(user_message)

    return await handle_tool_call_async(
        llm=llm,
        pocket=pocket,
        model=MODEL_NAME,
        tool_specs=tool_specs,
        messages=messages
    )


def upload(
        name: str, language: str, code: str, auth_provider: str = None, auth_handler: str = None, scopes=None,
        dependencies: str = None, upload_to_github: bool = False, *args, **kwargs):
    def _name_is_valid(_name):
        return bool(re.search(r'[^a-zA-Z_]', _name)) and _name is not None and _name != ""

    if _name_is_valid(name):
        raise gr.Error(
            message="Name isn't valid. shouldn't be empty and shouldn't include other characters except for (a-zA-Z_)",
            duration=3)

    if dependencies == "":
        dependencies = None
    elif dependencies is not None:
        dependencies = dependencies.split("\n")

    base_path = pathlib.Path(f"./tools/").resolve()
    tool_name = f"{name}_guess_bulls_and_cows"
    tool_path = base_path / tool_name
    tool_description = f"{name}'s guessing of bulls and cows number"

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

    add_tool(uploaded_tool_name, uploaded_tool_path)

    try:
        init_model()
    except Exception as e:
        delete_tool(uploaded_tool_name)
        init_model()
        raise gr.Error(f"failed to init model. {str(e)}", duration=5)

    return True


def build_upload_ui(state):
    AUTH_PROVIDERS = [None, "google", "slack", "github"]
    AUTH_HANDLERS = {
        None: [],
        "google": ["google-oauth2"],
        "slack": ["slack-oauth2", "slack-token"],
        "github": ["github-oauth2", "github-token"],
    }

    def _build_code_ui(language: str):
        return gr.Code(
            get_template(language),
            language=language,
            interactive=True,
            lines=20)

    def _build_auth_handlers(selected_provider, selected_handler):
        handler_list = AUTH_HANDLERS.get(selected_provider, [])
        return gr.update(choices=handler_list, value=handler_list[0] if len(handler_list) > 0 else None)

    with gr.Blocks() as upload_ui:
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
                upload,
                inputs=[name, selected_langauge, code_ui, auth_provider_ui, auth_handler_ui, scopes, dependencies_ui,
                        upload_to_github, state["is_tool_list_refresh_needed"]],
                outputs=[state["is_tool_list_refresh_needed"]]
            )

            selected_langauge.change(
                _build_code_ui, selected_langauge, code_ui,
            )
    return upload_ui


def build_chat_ui(state):
    PRE_LOADED_TOOL_NUM = 100

    def _refresh_tool_list_ui(tool_path, is_tool_list_refresh_needed):
        tool_values = list(tools.values())
        updated_tool_row = []
        updated_tool_text = []
        updated_tool_path = None if is_tool_list_refresh_needed else tool_path

        if not is_tool_list_refresh_needed:
            return tool_path, is_tool_list_refresh_needed, \
                *([gr.update()] * PRE_LOADED_TOOL_NUM), \
                *([gr.update()] * PRE_LOADED_TOOL_NUM)

        for i in range(PRE_LOADED_TOOL_NUM):
            if i < len(tool_values):
                updated_tool_row.append(
                    gr.update(visible=True)
                )
                updated_tool_text.append(
                    gr.update(value=tool_values[i])
                )
            else:
                updated_tool_row.append(gr.update(visible=False))
                updated_tool_text.append(gr.update(value=None))

        return updated_tool_path, False, *updated_tool_row, *updated_tool_text

    def _add_tool(tool_path):
        add_tool(tool_path, tool_path)
        try:
            init_model()
        except Exception as e:
            delete_tool(tool_path)
            init_model()
            raise gr.Error(f"failed to init model. {str(e)}", duration=5)

    def _add_tool_action(tool_path):
        _add_tool(tool_path)
        updated_tool_path, _, *updated = _refresh_tool_list_ui(tool_path, True)
        return updated_tool_path, *updated

    def _delete_tool_action(tool_path):
        if str(tool_path) not in tools.values():
            print(f"not found {tool_path} in tools. tools: {tools}")
            is_tool_list_refresh_needed = False
        else:
            delete_tool(tool_path)
            print(f"deleted {tool_path} in tools. tools: {tools}")
            is_tool_list_refresh_needed = True

        updated_tool_path, _, *updated = _refresh_tool_list_ui(tool_path, is_tool_list_refresh_needed)
        return updated_tool_path, *updated

    with gr.Blocks() as ui:
        with gr.Accordion(label="Tool list", open=False):
            with gr.Column():
                tool_row_list = []
                tool_text_list = []
                tool_delete_button_list = []

                tool_values = list(tools.values())
                for i in range(PRE_LOADED_TOOL_NUM):
                    if i < len(tool_values):
                        with gr.Row(visible=True, equal_height=True) as tool_row:
                            tool_text = gr.Text(value=tool_values[i], show_label=False, scale=1, container=False)
                            tool_delete_button = gr.Button("X", scale=0, size="lg", min_width=10)
                    else:
                        with gr.Row(visible=False, equal_height=True) as tool_row:
                            tool_text = gr.Text(show_label=False, scale=1, container=False)
                            tool_delete_button = gr.Button("X", scale=0, size="lg", min_width=10)

                    tool_row_list.append(tool_row)
                    tool_text_list.append(tool_text)
                    tool_delete_button_list.append(tool_delete_button)

                add_tool_button = gr.Textbox(placeholder="write your tool path down here to add tool manually",
                                             label="Add existing tool")

            for tool_text, tool_delete_button in zip(tool_text_list, tool_delete_button_list):
                tool_delete_button.click(
                    _delete_tool_action,
                    inputs=[tool_text],
                    outputs=[tool_text, *tool_row_list, *tool_text_list]
                )

            add_tool_button.submit(_add_tool_action, inputs=[add_tool_button],
                                   outputs=[add_tool_button, *tool_row_list, *tool_text_list])
            state["is_tool_list_refresh_needed"].change(
                _refresh_tool_list_ui,
                inputs=[add_tool_button, state["is_tool_list_refresh_needed"]],
                outputs=[add_tool_button, state["is_tool_list_refresh_needed"], *tool_row_list, *tool_text_list],
            )

        gr.ChatInterface(fn=chat, type="messages")

        ui.load(
            lambda x: _refresh_tool_list_ui(x, True),
            inputs=[add_tool_button],
            outputs=[add_tool_button, state["is_tool_list_refresh_needed"], *tool_row_list, *tool_text_list],
        )
    return ui


def ui():
    with gr.Blocks(
            theme=gr.themes.Default(text_size=gr.themes.sizes.text_lg,
                                    spacing_size=gr.themes.sizes.spacing_lg)
    ) as ui:
        state = {
            "is_tool_list_refresh_needed": gr.State(value=True)
        }

        with gr.Tab("chatbot"):
            build_chat_ui(state)

        with gr.Tab("tool register"):
            build_upload_ui(state)

    ui.launch()


if __name__ == "__main__":
    init_model()
    loop = asyncio.new_event_loop()
    loop.create_task(ui())
