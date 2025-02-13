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
        except Exception as e:
            logger.error(f"Error accessing assistants directory: {e}")

    def get_assistant(self, name: str) -> Optional[Assistant]:
        """Get an assistant by name"""
        return self.assistants.get(name)

    def select_assistant(self, message: str) -> Assistant:
        """Select appropriate assistant based on message content"""
        # Default to agent-building-assistant if no specific match
        default_assistant = self.assistants.get('agent-building-assistant')
        
        # Add your logic here to select appropriate assistant based on message content
        # For example:
        message_lower = message.lower()
        
        if "code" in message_lower or "programming" in message_lower:
            return self.assistants.get('coding-assistant', default_assistant)
        elif "data" in message_lower or "analysis" in message_lower:
            return self.assistants.get('data-assistant', default_assistant)
        
        return default_assistant 