import os
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class Assistant:
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content
        self.system_message = {
            "role": "system",
            "content": content
        }

class AssistantManager:
    DEFAULT_ASSISTANT = "default-assistant"

    def __init__(self, assistants_dir: str = "assistants"):
        self.assistants_dir = assistants_dir
        self.assistants: Dict[str, Assistant] = {}
        self.load_assistants()

    def load_assistants(self):
        """Load all assistant files from the assistants directory"""
        try:
            for filename in os.listdir(self.assistants_dir):
                if filename.endswith('.txt'):
                    assistant_name = filename[:-4]  # Remove .txt extension
                    file_path = os.path.join(self.assistants_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            self.assistants[assistant_name] = Assistant(assistant_name, content)
                            logger.info(f"Loaded assistant: {assistant_name}")
                    except Exception as e:
                        logger.error(f"Error loading assistant {filename}: {e}")

            if self.DEFAULT_ASSISTANT not in self.assistants:
                logger.error(f"Default assistant '{self.DEFAULT_ASSISTANT}' not found")
                # Create a basic default assistant if file is missing
                self.assistants[self.DEFAULT_ASSISTANT] = Assistant(
                    self.DEFAULT_ASSISTANT,
                    "You are a helpful assistant that provides detailed responses and can use various tools to help users."
                )

        except Exception as e:
            logger.error(f"Error accessing assistants directory: {e}")
            # Ensure we always have a default assistant
            self.assistants[self.DEFAULT_ASSISTANT] = Assistant(
                self.DEFAULT_ASSISTANT,
                "You are a helpful assistant that provides detailed responses and can use various tools to help users."
            )

    def get_assistant(self, name: str) -> Optional[Assistant]:
        """Get an assistant by name"""
        return self.assistants.get(name)

    def select_assistant(self, message: str) -> Assistant:
        """Select appropriate assistant based on message content"""
        # Add your logic here to select appropriate assistant based on message content
        # For now, always return the default assistant
        return self.assistants[self.DEFAULT_ASSISTANT] 