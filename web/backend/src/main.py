from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletion
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from hyperpocket_openai import PocketOpenAI
from openai import OpenAI
from src.tools import (
    send_mail, take_a_picture, call_diffusion_model,
    get_slack_messages, post_slack_message
)
import os
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()

# Constants
MODEL_NAME = "gpt-4o"
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # React dev server
]

class Message(BaseModel):
    text: str = Field(..., description="Message text")

class ChatRequest(BaseModel):
    messages: List[Message] = Field(..., description="Chat history")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    tool_calls: Optional[List[Dict]] = Field(None, description="Tool calls made during processing")

class AddToolRequest(BaseModel):
    code: str = Field(..., description="Python code for the new tool")

class AddToolResponse(BaseModel):
    name: str = Field(..., description="Name of the added tool")
    message: str = Field(..., description="Success message")

class AIService:
    def __init__(self):
        self.pocket = None
        self.llm = None
        self.tool_specs = None
        self.tools = None
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
        }
        tool_list = [tool["tool"] for tool in self.tools.values()]
        
        # Initialize Hyperpocket and OpenAI
        self.pocket = PocketOpenAI(tools=tool_list)
        self.tool_specs = self.pocket.get_open_ai_tool_specs()
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def process_chat(self, messages: List[Message]) -> ChatResponse:
        """
        Process chat request and return response.
        
        Args:
            messages: List of message texts
            
        Returns:
            ChatResponse object containing AI response and tool calls
        """
        # Convert messages to OpenAI format
        openai_messages = []
        for i, msg in enumerate(messages):
            role = "user" if i % 2 == 0 else "assistant"
            openai_messages.append({
                "role": role,
                "content": msg.text
            })

        while True:
            response = self.llm.chat.completions.create(
                model=MODEL_NAME,
                messages=openai_messages,
                tools=self.tool_specs,
            )
            choice = response.choices[0]
            openai_messages.append(choice.message)

            if choice.finish_reason == "stop":
                break

            elif response.choices[0].finish_reason == "tool_calls":
                tool_calls: List[ChatCompletionMessageToolCall] = response.choices[0].message.tool_calls
                for tool_call in tool_calls:
                    tool_message = await self.pocket.ainvoke(tool_call)
                    openai_messages.append(tool_message)

        return ChatResponse(
            response=response.choices[0].message.content,
            tool_calls=response.choices[0].message.tool_calls
        )

# Initialize FastAPI app
app = FastAPI(
    title="Hyperpocket AI Chat API",
    description="API for interacting with AI chat service",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI service
ai_service = AIService()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat request and return AI response.
    
    Args:
        request: ChatRequest object containing chat history
        
    Returns:
        ChatResponse object containing AI response and tool calls
        
    Raises:
        HTTPException: If messages array is empty
    """
    try:
        if not request.messages:
            raise HTTPException(
                status_code=400, 
                detail="Messages array is required"
            )

        return await ai_service.process_chat(request.messages)

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/tools/add", response_model=AddToolResponse)
async def add_tool(request: AddToolRequest):
    """
    Add a new custom tool from provided Python code.
    
    Args:
        request: AddToolRequest containing the tool code
        
    Returns:
        AddToolResponse with tool name and success message
    """
    try:
        # Create a temporary module to execute the code
        module_code = request.code
        
        # Basic validation
        if "@function_tool" not in module_code:
            raise ValueError("Tool must be decorated with @function_tool")
        
        # Execute the code in a new namespace
        namespace = {}
        exec(module_code, namespace)
        
        # Find the function decorated with @function_tool
        tool_function = None
        for item in namespace.values():
            if callable(item) and hasattr(item, "_is_tool"):
                tool_function = item
                break
                
        if not tool_function:
            raise ValueError("No function_tool found in the code")
            
        # Get the function name
        tool_name = tool_function.__name__
        
        # Add to tools dictionary
        ai_service.tools[tool_name] = {"tool": tool_function}
        
        # Reinitialize the service to update tools
        ai_service.initialize()
        
        return AddToolResponse(
            name=tool_name,
            message=f"Successfully added tool: {tool_name}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to add tool: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3001,
        reload=True
    ) 