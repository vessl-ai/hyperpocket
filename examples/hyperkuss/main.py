import os
import sys
import argparse

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(project_root)

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from hyperkuss.slack_manager import SlackManager
from hyperkuss.ai_service import AIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('main.py'):
            logger.info("Code changed. Restarting...")
            args = sys.argv[1:]  # Preserve command line arguments for restart
            os.execv(sys.executable, ['python'] + sys.argv)

def setup_hot_reload():
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()
    return observer

def parse_args():
    parser = argparse.ArgumentParser(description='HyperKuss Slack Bot')
    parser.add_argument('--reload', action='store_true', help='Enable hot reload for development')
    return parser.parse_args()

async def main():
    args = parse_args()
    
    # Initialize the AI service
    ai_service = AIService()

    # Initialize the Slack manager
    slack_manager = SlackManager(
        bot_token=os.environ["SLACK_BOT_TOKEN"],
        app_token=os.environ["SLACK_APP_TOKEN"],
        ai_service=ai_service
    )

    # Setup hot reload if flag is provided
    observer = None
    if args.reload:
        observer = setup_hot_reload()
        logger.info("Hot reload enabled")
    
    try:
        await slack_manager.start()
    except KeyboardInterrupt:
        await slack_manager.stop()
        if observer:
            observer.stop()
            observer.join()
        sys.exit(0)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
