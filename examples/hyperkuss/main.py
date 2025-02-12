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
import re
from hyperpocket.tool.function import FunctionTool
from hyperpocket_openai import PocketOpenAI
from slack_sdk.models.blocks import ButtonElement, ActionsBlock, SectionBlock
import json
from examples.hyperkuss.slack_manager import SlackManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class AIService:
    def __init__(self):
        self.pocket = None
        self.llm = None
        self.tool_specs = None
        self.tools = None
        self.custom_tools = {}
        self.initialize()

    def initialize(self):
        """Initialize AI service with tools and models."""
        if self.pocket:
            self.pocket._teardown_server()

        # Setup tools
        self.tools = {
            send_mail.name: {"tool": send_mail},
            take_a_picture.name: {"tool": take_a_picture},
            call_diffusion_model.name: {"tool": call_diffusion_model},
            get_slack_messages.name: {"tool": get_slack_messages},
            post_slack_message.name: {"tool": post_slack_message},
            get_channel_members.name: {"tool": get_channel_members},
            **self.custom_tools
        }

        # Create tool list
        tool_list = [tool["tool"] for tool in self.tools.values()]

        # Initialize Hyperpocket and OpenAI
        self.pocket = PocketOpenAI(tools=tool_list)
        self.tool_specs = self.pocket.get_open_ai_tool_specs()
        self.llm = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Initialize the AI service
ai_service = AIService()

# Initialize the Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize the Slack manager
slack_manager = SlackManager(app)

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

async def get_ai_response(messages, channel_id, thread_ts, say):
    """Get response from OpenAI with tool calling capabilities"""
    # Add system message
    full_messages = [{
        "role": "system",
        "content": "You are a helpful assistant that provides detailed responses and can use various tools to help users."
    }] + messages

    tool_calls = []
    openai_messages = full_messages.copy()

    while True:
        response = ai_service.llm.chat.completions.create(
            model="gpt-4o",
            messages=openai_messages,
            tools=ai_service.tool_specs,
            temperature=0.7,
            max_tokens=16384,
            presence_penalty=0.6,
            frequency_penalty=0.3
        )
        choice = response.choices[0]
        openai_messages.append(choice.message)

        if choice.finish_reason == "stop":
            break

        elif response.choices[0].finish_reason == "tool_calls":
            for tool_call in response.choices[0].message.tool_calls:
                # Send confirmation message with button
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                blocks = [
                    SectionBlock(
                        text=f"🔧 Request to use tool: *{tool_name}*\nArguments: ```{json.dumps(tool_args, indent=2)}```"
                    ),
                    ActionsBlock(
                        elements=[
                            ButtonElement(
                                text="✅ Approve",
                                action_id="approve_tool",
                                style="primary",
                                value=json.dumps({
                                    "tool_call_id": tool_call.id,
                                    "thread_ts": thread_ts
                                })
                            ),
                            ButtonElement(
                                text="❌ Deny",
                                action_id="deny_tool",
                                style="danger",
                                value=json.dumps({
                                    "tool_call_id": tool_call.id,
                                    "thread_ts": thread_ts
                                })
                            )
                        ]
                    )
                ]
                
                say(
                    text="Tool execution requires approval",
                    blocks=blocks,
                    thread_ts=thread_ts
                )
                
                # Store tool call for later use
                if thread_ts not in tool_calls_store:
                    tool_calls_store[thread_ts] = {}
                tool_calls_store[thread_ts][tool_call.id] = {
                    "tool_call": tool_call,
                    "pending": True,
                    "messages": openai_messages.copy()
                }
                
                # Wait for human approval (handled by action handlers)
                return "I'm waiting for approval to use the requested tool. Please approve or deny the request."

    return response.choices[0].message.content

# Store for pending tool calls
tool_calls_store = {}

@app.action("approve_tool")
async def handle_approve_tool(ack, body, say):
    await ack()
    
    value = json.loads(body["actions"][0]["value"])
    thread_ts = value["thread_ts"]
    tool_call_id = value["tool_call_id"]
    
    if thread_ts in tool_calls_store and tool_call_id in tool_calls_store[thread_ts]:
        stored_data = tool_calls_store[thread_ts][tool_call_id]
        if stored_data["pending"]:
            # Execute the tool
            tool_call = stored_data["tool_call"]
            tool_message = await ai_service.pocket.ainvoke(tool_call)
            
            # Update conversation with tool result
            stored_data["messages"].append(tool_message)
            
            # Get AI response with tool result
            response = ai_service.llm.chat.completions.create(
                model="gpt-4o",
                messages=stored_data["messages"],
                temperature=0.7,
                max_tokens=16384
            )
            
            # Send the response
            formatted_response = format_for_slack(response.choices[0].message.content)
            message_chunks = split_message(formatted_response)
            
            for chunk in message_chunks:
                say(
                    text=chunk,
                    thread_ts=thread_ts,
                    mrkdwn=True
                )
            
            # Clean up
            stored_data["pending"] = False

@app.action("deny_tool")
async def handle_deny_tool(ack, body, say):
    await ack()
    
    value = json.loads(body["actions"][0]["value"])
    thread_ts = value["thread_ts"]
    tool_call_id = value["tool_call_id"]
    
    if thread_ts in tool_calls_store and tool_call_id in tool_calls_store[thread_ts]:
        stored_data = tool_calls_store[thread_ts][tool_call_id]
        if stored_data["pending"]:
            say(
                text="❌ Tool execution was denied. Let me try to help without using the tool.",
                thread_ts=thread_ts
            )
            stored_data["pending"] = False

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
async def handle_message_events(event, say):
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

        # Get AI response with tool support
        ai_response = await get_ai_response(
            session.messages,
            channel_id,
            thread_ts,
            say
        )
        
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

        for chunk in message_chunks:
            if first_message:
                response = say(
                    text=chunk,
                    thread_ts=thread_ts,
                    mrkdwn=True
                )
                first_message = False
            else:
                say(
                    text=chunk,
                    thread_ts=thread_ts,
                    mrkdwn=True
                )

        # Add bot response to session history
        session.messages.append({
            "role": "assistant",
            "content": ai_response
        })
    except Exception as e:
        error_message = f"Sorry, I encountered an error: {str(e)}"
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
