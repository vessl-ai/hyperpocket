import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from openai import OpenAI
import sys
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from hyperpocket_openai import PocketOpenAI
from hyperpocket.tool import function_tool
from examples.hyperkuss.slack_manager import SlackManager
from examples.hyperkuss.assistant_manager import AssistantManager
from examples.hyperkuss.tool_manager import ToolManager
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class AIService:
    def __init__(self):
        self.pocket = None
        self.llm = None
        self.tool_manager = ToolManager()
        self.assistant_manager = AssistantManager()
        self.current_assistant = None  # Store explicitly chosen assistant
        self.initialize()

    def initialize(self):
        """Initialize AI service with tools and models."""
        if self.pocket:
            self.pocket._teardown_server()

        # Setup tools
        default_tools = [
            self.list_assistants,  # The decorator converts these methods to FunctionTools
            self.choose_assistant
        ]
        self.tool_manager.register_tools(default_tools)

        # Initialize Hyperpocket and OpenAI
        self.pocket = PocketOpenAI(tools=self.tool_manager.get_all_tools())
        self.tool_manager.update_tool_specs(self.pocket)
        self.llm = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def register_tool(self, tool):
        """Register a tool and reinitialize"""
        self.tool_manager.register_tool(tool)
        self.initialize()

    @function_tool()
    def list_assistants(self) -> List[str]:
        """Tool function to list available assistants"""
        return list(self.assistant_manager.assistants.keys())

    @function_tool()
    def choose_assistant(self, assistant_name: str) -> str:
        """Tool function to explicitly choose an assistant"""
        assistant = self.assistant_manager.get_assistant(assistant_name)
        if not assistant:
            available = ", ".join(self.list_assistants())
            return f"Assistant '{assistant_name}' not found. Available assistants: {available}"
        
        # Store the chosen assistant in the context
        self.current_assistant = assistant
        return f"Switched to assistant: {assistant_name}"

    async def get_response(self, messages, tool_calls_store=None):
        """Get response from OpenAI with tool calling capabilities"""
        # Use explicitly chosen assistant if available, otherwise select based on message
        assistant = self.current_assistant
        if not assistant:
            user_message = messages[-1]["content"] if messages else ""
            assistant = self.assistant_manager.select_assistant(user_message)
        
        # Add system message from selected assistant
        full_messages = [assistant.system_message] + messages

        tool_calls = []
        openai_messages = full_messages.copy()

        while True:
            response = self.llm.chat.completions.create(
                model="gpt-4o",
                messages=openai_messages,
                tools=self.tool_manager.tool_specs,
                temperature=0.7,
                max_tokens=16384,
                presence_penalty=0.6,
                frequency_penalty=0.3
            )
            choice = response.choices[0]
            openai_messages.append(choice.message)

            if choice.finish_reason == "stop":
                return response.choices[0].message.content

            elif response.choices[0].finish_reason == "tool_calls":
                return response.choices[0].message.tool_calls, openai_messages

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('main.py'):
            logger.info("Code changed. Restarting...")
            os.execv(sys.executable, ['python'] + sys.argv)

def setup_hot_reload():
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    return observer

def main():
    # Initialize the AI service
    ai_service = AIService()

    # Initialize the Slack app
    app = App(token=os.environ["SLACK_BOT_TOKEN"])

    # Initialize the Slack manager with AI service
    slack_manager = SlackManager(app, ai_service)

    # Setup hot reload in development
    if os.environ.get('ENVIRONMENT') != 'production':
        observer = setup_hot_reload()
        logger.info("Hot reload enabled")
    
    # Initialize the Socket Mode Handler
    handler = SocketModeHandler(
        app=app,
        app_token=os.environ["SLACK_APP_TOKEN"]
    )
    
    print("⚡️ Bolt app is running!")
    print("💡 Invite the bot to channels using: /invite @HyperKuss")
    
    try:
        handler.start()
    except KeyboardInterrupt:
        if os.environ.get('ENVIRONMENT') != 'production':
            observer.stop()
            observer.join()
        sys.exit(0)

if __name__ == "__main__":
    main()
