from slack_bolt import App
from slack_sdk.models.blocks import ButtonElement, ActionsBlock, SectionBlock
import json
import re
import logging

logger = logging.getLogger(__name__)

class SlackManager:
    def __init__(self, app: App, ai_service):
        self.app = app
        self.ai_service = ai_service
        self.sessions = {}  # Format: {thread_ts: ConversationState}
        self.tool_calls_store = {}
        self.setup_handlers()

    def setup_handlers(self):
        @self.app.event("message")
        async def handle_message_events(event, say):
            """Handle incoming message events"""
            # Ignore bot messages to prevent loops
            if event.get("bot_id"):
                return

            thread_ts = event.get("thread_ts", event.get("ts"))
            channel_id = event["channel"]
            
            # Get or create session for this thread
            if thread_ts not in self.sessions:
                self.sessions[thread_ts] = ConversationState()
                # Fetch thread history if this is a reply in an existing thread
                if thread_ts != event.get("ts"):
                    thread_messages = self.get_thread_history(event["channel"], thread_ts)
                    self.sessions[thread_ts].messages.extend(thread_messages)
            
            session = self.sessions[thread_ts]
            
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
                ai_response = await self.process_ai_response(
                    session.messages,
                    channel_id,
                    thread_ts,
                    say
                )
                
                # If assistant changed, add an indicator in the response
                if session.current_assistant != self.ai_service.assistant_manager.select_assistant(event["text"]):
                    session.current_assistant = self.ai_service.assistant_manager.select_assistant(event["text"])
                    assistant_indicator = f"_Switched to {session.current_assistant.name}_\n\n"
                    ai_response = assistant_indicator + ai_response
                
                # Format response for Slack
                formatted_response = self.format_for_slack(ai_response)
                
                # Delete thinking message
                self.app.client.chat_delete(
                    channel=channel_id,
                    ts=thinking_msg['ts']
                )

                # Split and send response in chunks
                message_chunks = self.split_message(formatted_response)
                first_message = True

                for chunk in message_chunks:
                    if first_message:
                        say(
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
                        self.app.client.chat_delete(
                            channel=channel_id,
                            ts=thinking_msg['ts']
                        )
                    except:
                        pass
                say(
                    text=error_message,
                    thread_ts=thread_ts
                )

        @self.app.action("approve_tool")
        async def handle_approve_tool(ack, body, say):
            await ack()
            await self._handle_tool_approval(body, say, approved=True)

        @self.app.action("deny_tool")
        async def handle_deny_tool(ack, body, say):
            await ack()
            await self._handle_tool_approval(body, say, approved=False)

    def get_thread_history(self, channel_id, thread_ts):
        """Fetch all messages in a thread"""
        try:
            result = self.app.client.conversations_replies(
                channel=channel_id,
                ts=thread_ts
            )
            messages = []
            for msg in result['messages']:
                if 'bot_id' in msg and "Thinking..." in msg.get('text', ''):
                    continue
                    
                role = "assistant" if 'bot_id' in msg else "user"
                messages.append({
                    "role": role,
                    "content": msg['text']
                })
            return messages
        except Exception as e:
            logger.error(f"Error fetching thread history: {e}")
            return []

    async def _handle_tool_approval(self, body, say, approved: bool):
        value = json.loads(body["actions"][0]["value"])
        thread_ts = value["thread_ts"]
        tool_call_id = value["tool_call_id"]
        
        if thread_ts in self.tool_calls_store and tool_call_id in self.tool_calls_store[thread_ts]:
            stored_data = self.tool_calls_store[thread_ts][tool_call_id]
            if stored_data["pending"]:
                if approved:
                    # Execute the tool and handle response
                    await self._execute_approved_tool(stored_data, thread_ts, say)
                else:
                    say(
                        text="❌ Tool execution was denied. Let me try to help without using the tool.",
                        thread_ts=thread_ts
                    )
                stored_data["pending"] = False

    @staticmethod
    def split_message(text, max_length=3000):
        """Split a long message into smaller chunks"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
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

    @staticmethod
    def format_for_slack(text):
        """Format text for Slack's mrkdwn"""
        lines = text.split('\n')
        formatted_lines = []
        in_code_block = False
        
        for line in lines:
            if line.startswith('```'):
                if in_code_block:
                    formatted_lines.append('```')
                    in_code_block = False
                else:
                    formatted_lines.append('```')
                    in_code_block = True
                continue
            
            if not in_code_block:
                line = re.sub(r'\*\*(.+?)\*\*', r'*\1*', line)
                line = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'_\1_', line)
                line = re.sub(r'`(.+?)`', r'` \1 `', line)
                
                if line.strip().startswith('- ') or line.strip().startswith('* '):
                    line = '•' + line[1:]
                
                if re.match(r'^\d+\.', line.strip()):
                    line = '  ' + line
                
                line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<\2|\1>', line)
            
            formatted_lines.append(line)
        
        text = '\n'.join(formatted_lines)
        text = re.sub(r'\n\s*```', '\n```', text)
        
        return text

    async def _execute_approved_tool(self, stored_data, thread_ts, say):
        """Execute an approved tool and handle its response"""
        tool_call = stored_data["tool_call"]
        tool_message = await self.ai_service.pocket.ainvoke(tool_call)
        
        # Update conversation with tool result
        stored_data["messages"].append(tool_message)
        
        # Get AI response with tool result
        response = self.ai_service.llm.chat.completions.create(
            model="gpt-4o",
            messages=stored_data["messages"],
            temperature=0.7,
            max_tokens=16384
        )
        
        # Send the response
        formatted_response = self.format_for_slack(response.choices[0].message.content)
        message_chunks = self.split_message(formatted_response)
        
        for chunk in message_chunks:
            say(
                text=chunk,
                thread_ts=thread_ts,
                mrkdwn=True
            )

    async def process_ai_response(self, messages, channel_id, thread_ts, say):
        """Process AI response and handle tool calls if any"""
        result = await self.ai_service.get_response(messages, self.tool_calls_store)
        
        if isinstance(result, tuple):  # Tool calls
            tool_calls, messages = result
            for tool_call in tool_calls:
                tool_args = json.loads(tool_call.function.arguments)
                
                blocks = [
                    SectionBlock(
                        text=f"🔧 Request to use tool: *{tool_call.function.name}*\nArguments: ```{json.dumps(tool_args, indent=2)}```"
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
                
                if thread_ts not in self.tool_calls_store:
                    self.tool_calls_store[thread_ts] = {}
                self.tool_calls_store[thread_ts][tool_call.id] = {
                    "tool_call": tool_call,
                    "pending": True,
                    "messages": messages.copy()
                }
                
                return "I'm waiting for approval to use the requested tool. Please approve or deny the request."
        
        return result  # Regular response

class ConversationState:
    def __init__(self):
        self.messages = []
        self.context = {}
        self.current_assistant = None

    def __str__(self):
        return f"ConversationState(messages={self.messages}, context={self.context}, current_assistant={self.current_assistant})" 