import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from typing import Dict
from dotenv import load_dotenv
from openai import OpenAI
import sys
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import re  # Add this to imports at the top

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Initialize the Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Store conversation sessions
# Format: {thread_ts: ConversationState}
sessions: Dict[str, dict] = {}

class ConversationState:
    def __init__(self):
        self.messages = []
        self.context = {}

def get_thread_history(client, channel_id, thread_ts):
    """Fetch all messages in a thread"""
    try:
        result = client.conversations_replies(
            channel=channel_id,
            ts=thread_ts
        )
        messages = []
        for msg in result['messages']:
            # Skip the current bot's messages if they're temporary "thinking" messages
            if 'bot_id' in msg and "Thinking..." in msg.get('text', ''):
                continue
                
            # Add message with appropriate role
            role = "assistant" if 'bot_id' in msg else "user"
            messages.append({
                "role": role,
                "content": msg['text']
            })
        return messages
    except Exception as e:
        logger.error(f"Error fetching thread history: {e}")
        return []

def get_ai_response(messages):
    """Get response from OpenAI"""
    # Add system message to encourage detailed responses
    full_messages = [{
        "role": "system",
        "content": "You are a helpful assistant that provides detailed and comprehensive responses. Feel free to use multiple paragraphs when needed to fully explain concepts."
    }] + messages

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=full_messages,
        temperature=0.7,
        max_tokens=16384,  # Increased from 1000
        presence_penalty=0.6,  # Encourage more diverse responses
        frequency_penalty=0.3  # Reduce repetition
    )
    return response.choices[0].message.content

def split_message(text, max_length=3000):
    """Split a long message into smaller chunks"""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= max_length:
            current_chunk += (paragraph + '\n\n')
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + '\n\n'
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def format_for_slack(text):
    """Format text for Slack's mrkdwn"""
    # Replace code blocks
    lines = text.split('\n')
    formatted_lines = []
    in_code_block = False
    
    for line in lines:
        # Handle code blocks
        if line.startswith('```'):
            if in_code_block:
                formatted_lines.append('```')
                in_code_block = False
            else:
                # For Slack, we don't need language identifier
                formatted_lines.append('```')
                in_code_block = True
            continue
        
        if not in_code_block:
            # Handle bold: Convert ** to * for Slack's bold
            line = re.sub(r'\*\*(.+?)\*\*', r'*\1*', line)
            
            # Handle italics: Convert remaining single * to _
            line = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'_\1_', line)
            
            # Handle inline code: Add spaces around backticks for better visibility
            line = re.sub(r'`(.+?)`', r'` \1 `', line)
            
            # Handle bullet points: standardize on •
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                line = '•' + line[1:]
            
            # Handle numbered lists: add extra space for better readability
            if re.match(r'^\d+\.', line.strip()):
                line = '  ' + line
            
            # Handle links: [text](url) -> <url|text>
            line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<\2|\1>', line)
        
        formatted_lines.append(line)
    
    # Join lines and handle any double line breaks
    text = '\n'.join(formatted_lines)
    
    # Clean up any extra spaces around code blocks
    text = re.sub(r'\n\s*```', '\n```', text)
    
    return text

@app.event("message")
def handle_message_events(event, say):
    """Handle incoming message events"""
    # Ignore bot messages to prevent loops
    if event.get("bot_id"):
        return

    thread_ts = event.get("thread_ts", event.get("ts"))
    channel_id = event["channel"]
    
    # Get or create session for this thread
    if thread_ts not in sessions:
        sessions[thread_ts] = ConversationState()
        # Fetch thread history if this is a reply in an existing thread
        if thread_ts != event.get("ts"):
            thread_messages = get_thread_history(app.client, event["channel"], thread_ts)
            sessions[thread_ts].messages.extend(thread_messages)
    
    session = sessions[thread_ts]
    
    # Add current message to session history
    session.messages.append({
        "role": "user",
        "content": event["text"]
    })

    try:
        # Send a temporary "thinking" message
        thinking_msg = say(
            text="🤔 Thinking...",
            thread_ts=thread_ts
        )

        # Get AI response
        ai_response = get_ai_response(session.messages)
        
        # Format response for Slack
        formatted_response = format_for_slack(ai_response)
        
        # Delete thinking message
        app.client.chat_delete(
            channel=channel_id,
            ts=thinking_msg['ts']
        )

        # Split and send response in chunks
        message_chunks = split_message(formatted_response)
        first_message = True
        first_message_ts = None

        for chunk in message_chunks:
            if first_message:
                response = say(
                    text=chunk,
                    thread_ts=thread_ts,
                    mrkdwn=True  # Enable markdown formatting
                )
                first_message_ts = response['ts']
                first_message = False
            else:
                say(
                    text=chunk,
                    thread_ts=thread_ts,
                    mrkdwn=True  # Enable markdown formatting
                )

        # Add bot response to session history (unformatted version)
        session.messages.append({
            "role": "assistant",
            "content": ai_response
        })
    except Exception as e:
        error_message = f"Sorry, I encountered an error: {str(e)}"
        # Delete thinking message if it exists
        if 'thinking_msg' in locals():
            try:
                app.client.chat_delete(
                    channel=channel_id,
                    ts=thinking_msg['ts']
                )
            except:
                pass
            
        say(
            text=error_message,
            thread_ts=thread_ts
        )

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
