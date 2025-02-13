from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_sdk.models.blocks import ButtonElement, ActionsBlock, SectionBlock
import json
import re
import logging

logger = logging.getLogger(__name__)

class SlackManager:
    def __init__(self, bot_token: str, app_token: str, ai_service):
        self.app = AsyncApp(token=bot_token)
        self.app_token = app_token
        self.ai_service = ai_service
        self.sessions = {}  # Format: {thread_ts: ConversationState}
        self.tool_calls_store = {}
        self.handler = None
        self.setup_handlers()

    def setup_handlers(self):
        @self.app.event("message")
        async def handle_message_events(body, event, say, logger):
            """Handle incoming message events"""
            try:
                # Ignore bot messages to prevent loops
                if event.get("bot_id"):
                    return

                # Check if the event has text
                if "text" not in event:
                    logger.warning("Received message event without text")
                    return

                # Check if we have required fields
                if "channel" not in event:
                    logger.warning("Received message event without channel")
                    return

                # Get thread info
                thread_ts = event.get("thread_ts", event.get("ts"))
                if not thread_ts:
                    logger.warning("Received message event without thread_ts or ts")
                    return

                channel_id = event["channel"]
                message_text = event["text"]
                
                # Initialize session if needed
                if thread_ts not in self.sessions:
                    self.sessions[thread_ts] = ConversationState()
                
                session = self.sessions[thread_ts]

                # Fetch thread history if this is a reply in an existing thread
                if thread_ts != event.get("ts") and not session.messages:
                    thread_messages = await self.get_thread_history(channel_id, thread_ts)
                    session.messages.extend(thread_messages)
                
                # Add current message to session history
                session.messages.append({
                    "role": "user",
                    "content": message_text
                })

                # Send a temporary "thinking" message
                thinking_msg = await say(
                    text="🤔 Thinking...",
                    thread_ts=thread_ts
                )

                try:
                    # Get AI response with tool support
                    ai_response = await self.process_ai_response(
                        session.messages,
                        channel_id,
                        thread_ts,
                        say
                    )
                    
                    # Format response for Slack
                    formatted_response = self.format_for_slack(ai_response)
                    
                    # Delete thinking message
                    await self.app.client.chat_delete(
                        channel=channel_id,
                        ts=thinking_msg['ts']
                    )

                    # Split and send response in chunks
                    message_chunks = self.split_message(formatted_response)
                    
                    for chunk in message_chunks:
                        await say(
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
                    logger.error(f"Error processing message: {str(e)}")
                    if thinking_msg:
                        try:
                            await self.app.client.chat_delete(
                                channel=channel_id,
                                ts=thinking_msg['ts']
                            )
                        except:
                            pass
                    await say(
                        text=f"Sorry, I encountered an error: {str(e)}",
                        thread_ts=thread_ts
                    )

            except Exception as e:
                logger.error(f"Error in message handler: {str(e)}")
                await say(
                    text=f"Sorry, I encountered an error: {str(e)}",
                    thread_ts=thread_ts if 'thread_ts' in locals() else None
                )

        @self.app.action("approve_tool")
        async def handle_approve_tool(ack, body, say):
            await ack()
            await self._handle_tool_approval(body, say, approved=True)

        @self.app.action("deny_tool")
        async def handle_deny_tool(ack, body, say):
            await ack()
            await self._handle_tool_approval(body, say, approved=False)

    async def start(self):
        """Start the Slack app"""
        self.handler = AsyncSocketModeHandler(
            app=self.app,
            app_token=self.app_token
        )
        
        print("⚡️ Bolt app is running!")
        print("💡 Invite the bot to channels using: /invite @HyperKuss")
        
        await self.handler.start_async()

    async def stop(self):
        """Stop the Slack app"""
        if self.handler:
            await self.handler.close()

    async def get_thread_history(self, channel_id, thread_ts):
        """Fetch all messages in a thread"""
        try:
            result = await self.app.client.conversations_replies(
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

    async def process_ai_response(self, messages, channel_id, thread_ts, say):
        """Process AI response and handle tool calls if any"""
        response, tool_calls = await self.ai_service.get_response(messages, thread_ts)
        
        if tool_calls:  # Tool calls need approval
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
                
                await say(
                    text="Tool execution requires approval",
                    blocks=blocks,
                    thread_ts=thread_ts
                )

        return response

    async def _handle_tool_approval(self, body, say, approved: bool):
        """Handle tool approval/denial"""
        try:
            value = json.loads(body["actions"][0]["value"])
            thread_ts = value["thread_ts"]
            tool_call_id = value["tool_call_id"]
            
            logger.info(f"Tool {'approval' if approved else 'denial'} received - thread: {thread_ts}, tool_call_id: {tool_call_id}")
            
            # Get the session
            session = self.sessions.get(thread_ts)
            if not session:
                logger.error(f"Session not found for thread: {thread_ts}")
                await say(
                    text="Sorry, I couldn't find the conversation context.",
                    thread_ts=thread_ts
                )
                return

            if approved:
                logger.info(f"Executing approved tool: {tool_call_id}")
                # Send thinking message
                thinking_msg = await say(
                    text="🤔 Executing tool...",
                    thread_ts=thread_ts
                )

                try:
                    response = await self.ai_service.execute_approved_tool(thread_ts, tool_call_id)
                    logger.info(f"Tool execution response received - length: {len(response) if response else 0}")
                    
                    if response:
                        # Delete thinking message
                        await self.app.client.chat_delete(
                            channel=body["channel"]["id"],
                            ts=thinking_msg['ts']
                        )

                        # Format and send response
                        formatted_response = self.format_for_slack(response)
                        message_chunks = self.split_message(formatted_response)
                        logger.info(f"Sending response in {len(message_chunks)} chunks")
                        
                        for chunk in message_chunks:
                            await say(
                                text=chunk,
                                thread_ts=thread_ts,
                                mrkdwn=True
                            )

                        # Add tool response to conversation history
                        session.messages.append({
                            "role": "assistant",
                            "content": response
                        })
                        logger.info("Tool response added to conversation history")
                    else:
                        logger.error("Tool execution returned no response")
                        await say(
                            text="Sorry, I couldn't process the tool execution.",
                            thread_ts=thread_ts
                        )
                except Exception as e:
                    logger.error(f"Error executing tool: {str(e)}", exc_info=True)
                    await say(
                        text=f"Sorry, I encountered an error while executing the tool: {str(e)}",
                        thread_ts=thread_ts
                    )
            else:
                logger.info("Processing tool denial")
                response = self.ai_service.deny_tool(thread_ts)
                if response:
                    await say(
                        text=response,
                        thread_ts=thread_ts
                    )
                    # Add denial response to conversation history
                    session.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                    logger.info("Denial response added to conversation history")

        except Exception as e:
            logger.error(f"Error in tool approval handler: {str(e)}", exc_info=True)
            await say(
                text=f"Sorry, I encountered an error: {str(e)}",
                thread_ts=thread_ts if 'thread_ts' in locals() else None
            )

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

class ConversationState:
    def __init__(self):
        self.messages = []
        self.context = {}
        self.current_assistant = None

    def __str__(self):
        return f"ConversationState(messages={self.messages}, context={self.context}, current_assistant={self.current_assistant})" 