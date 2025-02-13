import os
from openai import OpenAI
from hyperpocket_openai import PocketOpenAI
from hyperpocket.tool import function_tool
from typing import List, Dict, Any, Optional, Tuple
from hyperkuss.assistant_manager import AssistantManager
from hyperkuss.tool_manager import ToolManager
import logging
from hyperkuss.tools import AVAILABLE_TOOLS

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.pocket = None
        self.llm = None
        self.tool_manager = ToolManager()
        self.assistant_manager = AssistantManager()
        # Initialize with default assistant
        self.current_assistant = self.assistant_manager.get_assistant(self.assistant_manager.DEFAULT_ASSISTANT)
        self.pending_tool_calls: Dict[str, Dict[str, Any]] = {}
        
        # Setup initial tools
        default_tools = [
            self._create_list_assistants_tool(),
            self._create_choose_assistant_tool(),
            # Add all available tools from central registry
            *AVAILABLE_TOOLS
        ]
        self.tool_manager.register_tools(default_tools)
        
        # Initialize services
        self.initialize_services()

    def initialize_services(self):
        """Initialize OpenAI and PocketOpenAI services"""
        if self.pocket:
            self.pocket._teardown_server()

        # Initialize Hyperpocket and OpenAI
        self.pocket = PocketOpenAI(tools=self.tool_manager.get_all_tools())
        self.tool_manager.update_tool_specs(self.pocket)
        self.llm = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def _create_list_assistants_tool(self):
        """Create a tool function for listing assistants"""
        @function_tool()
        def list_assistants() -> List[str]:
            """Tool function to list available assistants"""
            return list(self.assistant_manager.assistants.keys())
        return list_assistants

    def _create_choose_assistant_tool(self):
        """Create a tool function for choosing assistant"""
        @function_tool()
        def choose_assistant(assistant_name: str) -> str:
            """Tool function to explicitly choose an assistant"""
            # First try exact match
            assistant = self.assistant_manager.get_assistant(assistant_name)
            
            if not assistant:
                # If no exact match, use GPT-4-mini to find best match
                try:
                    response = self.llm.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{
                            "role": "system",
                            "content": "You are a helpful assistant that matches user input to the closest assistant name."
                        }, {
                            "role": "user",
                            "content": f"""
                            Find the closest matching assistant name from this list:
                            {list(self.assistant_manager.assistants.keys())}
                            
                            User input: {assistant_name}
                            
                            Respond with just the matching name, or "none" if no good match found.
                            """
                        }],
                        temperature=0.3,
                        max_tokens=50
                    )
                    
                    suggested_name = response.choices[0].message.content.strip().lower()
                    if suggested_name != "none":
                        assistant = self.assistant_manager.get_assistant(suggested_name)

                except Exception as e:
                    logger.error(f"Error in assistant name matching: {str(e)}")
            
            if not assistant:
                available = ", ".join(list(self.assistant_manager.assistants.keys()))
                return f"Assistant '{assistant_name}' not found. Available assistants: {available}"
            
            # Store the chosen assistant in the context
            self.current_assistant = assistant
            return f"Switched to assistant: {assistant.name}"
        return choose_assistant

    async def get_response(self, messages, thread_ts: Optional[str] = None) -> Tuple[str, Optional[List[Dict[str, Any]]]]:
        """Get response from OpenAI with tool calling capabilities"""
        # Use explicitly chosen assistant if available, otherwise select based on message
        assistant = self.current_assistant
        if not assistant:
            user_message = messages[-1]["content"] if messages else ""
            assistant = self.assistant_manager.select_assistant(user_message)
        
        # Add system message from selected assistant
        full_messages = [assistant.system_message] + messages

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
                return response.choices[0].message.content, None

            elif response.choices[0].finish_reason == "tool_calls":
                tool_calls = response.choices[0].message.tool_calls
                if thread_ts:
                    # Store tool calls for approval
                    self.pending_tool_calls[thread_ts] = {
                        "tool_calls": tool_calls,
                        "messages": openai_messages.copy()
                    }
                    # Return message requesting approval and tool calls info
                    return "I need to use some tools to help you. Please approve or deny the tool usage.", tool_calls
                else:
                    # If no thread_ts (not in Slack), execute tools directly
                    for tool_call in tool_calls:
                        tool_message = await self.pocket.ainvoke(tool_call)
                        openai_messages.append(tool_message)

    async def execute_approved_tool(self, thread_ts: str, tool_call_id: str) -> Optional[str]:
        """Execute an approved tool and continue the conversation"""
        if thread_ts not in self.pending_tool_calls:
            logger.error(f"No pending tool calls found for thread: {thread_ts}")
            return None

        stored_data = self.pending_tool_calls[thread_ts]
        tool_calls = stored_data["tool_calls"]
        messages = stored_data["messages"]

        # Find the approved tool call
        tool_call = next((tc for tc in tool_calls if tc.id == tool_call_id), None)
        if not tool_call:
            logger.error(f"Tool call {tool_call_id} not found in pending calls")
            return None

        try:
            logger.info(f"Executing tool: {tool_call.function.name} with args: {tool_call.function.arguments}")
            # Execute the tool
            tool_message = await self.pocket.ainvoke(tool_call)
            logger.info(f"Tool execution result: {tool_message}")
            messages.append(tool_message)

            # Get AI response with tool result
            logger.info("Getting AI response with tool result")
            response = self.llm.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=self.tool_manager.tool_specs,  # Keep tools available for follow-up
                temperature=0.7,
                max_tokens=16384
            )

            # Clean up stored data
            del self.pending_tool_calls[thread_ts]
            logger.info("Tool execution completed successfully")
            
            return response.choices[0].message.content
        except Exception as e:
            # Clean up on error
            del self.pending_tool_calls[thread_ts]
            logger.error(f"Error during tool execution: {str(e)}", exc_info=True)
            raise e

    def deny_tool(self, thread_ts: str) -> Optional[str]:
        """Handle denied tool execution"""
        if thread_ts not in self.pending_tool_calls:
            return None

        # Clean up stored data
        del self.pending_tool_calls[thread_ts]
        
        return "Tool usage was denied. Let me try to help you without using tools."