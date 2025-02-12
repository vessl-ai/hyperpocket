from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletion
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from hyperpocket.tool.function import FunctionTool
from hyperpocket_openai import PocketOpenAI
from openai import OpenAI
from src.tools import (
    send_mail, take_a_picture, call_diffusion_model,
    get_slack_messages, post_slack_message, get_channel_members
)
import os
from typing import Dict, List, Optional
import inspect

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

class GenerateToolRequest(BaseModel):
    prompt: str = Field(..., description="Prompt for generating tool code")

class AIService:
    def __init__(self):
        self.pocket = None
        self.llm = None
        self.tool_specs = None
        self.tools = None
        self.custom_tools = {}
        self.github_tools = []  # Add this to store GitHub tool URLs
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
        
        # Create tool list including GitHub tools
        tool_list = [tool["tool"] for tool in self.tools.values()]
        tool_list.extend(self.github_tools)  # Add GitHub tool URLs
        
        # Initialize Hyperpocket and OpenAI
        self.pocket = PocketOpenAI(tools=tool_list)
        self.tool_specs = self.pocket.get_open_ai_tool_specs()
        self.llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def add_tool(self, name: str, tool_function: callable, code: str = None):
        """Add a new tool to the service."""
        self.custom_tools[name] = {
            "tool": tool_function,
            "code": code  # Store the original code
        }
        self.initialize()

    def add_github_tool(self, url: str):
        """Add a GitHub tool URL."""
        if url not in self.github_tools:
            self.github_tools.append(url)
            self.initialize()

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
        module_code = """
from hyperpocket.tool import function_tool
from hyperpocket.auth import AuthProvider

{}
""".format(request.code)
        
        # Basic validation
        if "@function_tool" not in module_code:
            raise ValueError("Tool must be decorated with @function_tool")
        
        # Execute the code in a new namespace
        namespace = {}
        exec(module_code, namespace)
        
        # Find the function decorated with @function_tool
        tool_function = None
        function_name = None
        
        # Find the first FunctionTool instance
        for name, item in namespace.items():
            if isinstance(item, FunctionTool):
                tool_function = item
                function_name = name
                break
                
        if not tool_function:
            raise ValueError("No function_tool found in the code. Make sure you're using the @function_tool decorator.")
            
        # Add the tool using the new method
        ai_service.add_tool(function_name, tool_function, request.code)
        
        return AddToolResponse(
            name=function_name,
            message=f"Successfully added tool: {function_name}. You can now use this tool in your conversations."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to add tool: {str(e)}"
        )

@app.get("/api/tools")
async def get_tools():
    """Get all registered tools and their specifications."""
    try:
        tools_info = []
        
        # Add regular tools
        for name, tool_data in ai_service.tools.items():
            tool = tool_data["tool"]
            func = tool.func if isinstance(tool, FunctionTool) else tool
            
            # Get docstring
            docstring = func.__doc__ or "No description available"
            docstring = inspect.cleandoc(docstring)
            
            # Split docstring into description and args sections
            parts = docstring.split("Args:")
            description = parts[0].strip()
            args_section = parts[1].strip() if len(parts) > 1 else ""
            
            # Check if tool is custom by checking if it's in custom_tools
            is_custom = name in ai_service.custom_tools
            
            # Check if tool is built-in by checking if it's one of the imported tools
            builtin_tools = [
                send_mail, take_a_picture, call_diffusion_model,
                get_slack_messages, post_slack_message, get_channel_members
            ]
            is_builtin = tool_data["tool"] in builtin_tools
            
            tool_info = {
                "name": name,
                "description": description,
                "parameters": [],
                "isCustom": not is_builtin  # Custom if it's not a built-in tool
            }
            
            # Get parameters from function signature
            if hasattr(func, "__annotations__"):
                for param_name, param_type in func.__annotations__.items():
                    if param_name != "return":
                        param_info = {
                            "name": param_name,
                            "type": str(param_type).replace("typing.", ""),
                            "description": args_section.split("\n")[0].strip() if param_name in args_section else "",
                            "required": True
                        }
                        tool_info["parameters"].append(param_info)
            
            tools_info.append(tool_info)
            
        # Add GitHub tools
        for url in ai_service.github_tools:
            tool_name = url.rstrip("/").split("/")[-1]
            tool_info = {
                "name": tool_name,
                "description": f"GitHub tool from: {url}",
                "parameters": [],
                "isCustom": True,
                "isGitHub": True,  # Add this flag
                "url": url  # Include the URL
            }
            tools_info.append(tool_info)
            
        return {"tools": tools_info}
        
    except Exception as e:
        print(f"Error getting tools: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tools: {str(e)}"
        )

@app.get("/api/tools/{tool_name}/code")
async def get_tool_code(tool_name: str):
    """Get the source code of a specific tool."""
    try:
        tool_data = ai_service.tools.get(tool_name)
        if not tool_data:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_name}' not found"
            )
            
        tool = tool_data["tool"]
        
        # For custom tools, return the original code used to create the tool
        if tool_name in ai_service.custom_tools:
            return {"code": ai_service.custom_tools[tool_name]["code"]}
        
        # For built-in tools, get the source from the original function
        if isinstance(tool, FunctionTool):
            func = tool.func
        else:
            func = tool
            
        code = inspect.getsource(func)
        return {"code": code}
        
    except Exception as e:
        print(f"Error getting tool code: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get tool code: {str(e)}"
        )

@app.post("/api/tools/from-git")
async def add_tool_from_git(request: dict):
    """Add a tool from a GitHub URL."""
    try:
        url = request["url"]
        
        # Basic validation
        if not url.startswith("https://github.com/"):
            raise HTTPException(
                status_code=400,
                detail="Invalid GitHub URL"
            )
        
        # Add the GitHub tool URL
        ai_service.add_github_tool(url)
        
        # Get the tool name from the URL
        tool_name = url.rstrip("/").split("/")[-1]
        
        return {
            "name": tool_name,
            "message": f"Successfully added GitHub tool: {tool_name}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to add tool from git: {str(e)}"
        )

@app.post("/api/tools/generate")
async def generate_tool_code(request: GenerateToolRequest):
    """Generate tool code from a prompt."""
    try:
        messages = [
            {"role": "system", "content": """You are a Python code generator. Generate code for a tool function that follows these rules:
1. Must use the @function_tool decorator (no need to import it)
2. Must have a clear docstring with Args section
3. Must have type hints for all parameters and return value
4. Must be a single function
5. Must be production-ready code (not just example code, but actual production code. use official sdk if available)
6. If the tool requires authentication:
   - Use auth_provider parameter in @function_tool decorator
   - The auth token will be automatically provided as a keyword argument
   - Do not manually handle authentication in the function
   
Available auth providers and their token names (also no need to import AuthProvider):
- Slack: auth_provider=AuthProvider.SLACK (token provided as SLACK_BOT_TOKEN)
- Gmail: auth_provider=AuthProvider.GOOGLE (token provided as SLACK_BOT_TOKEN)
- GitHub: auth_provider=AuthProvider.GITHUB (token provided as GITHUB_TOKEN)
- Notion: auth_provider=AuthProvider.NOTION (token provided as NOTION_TOKEN)
- And many more...

Example:
@function_tool(auth_provider=AuthProvider.SLACK)
def post_message(channel: str, message: str, **kwargs) -> str:
    '''Post a message to Slack channel
    
    Args:
        channel: The channel to post to
        message: The message to post
        SLACK_BOT_TOKEN: Automatically provided by the auth provider
    '''
    SLACK_BOT_TOKEN = kwargs["SLACK_BOT_TOKEN"]
    ...
"""},
            {"role": "user", "content": f"Generate only the Python code without any markdown or additional text for: {request.prompt}"}
        ]

        response = ai_service.llm.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
        )

        code = response.choices[0].message.content
        
        # Clean up the response
        code = code.lstrip('\n')  # Remove leading newlines
        code = code.strip()
        
        # Remove markdown code block if present
        if code.startswith('```python'):
            code = code[9:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]
            
        # Remove any additional notes or text after the code
        code = code.split('\n\n#')[0]  # Remove notes that start with #
        code = code.split('\n\nNote:')[0]  # Remove notes that start with "Note:"
        
        # Final cleanup of any remaining whitespace
        code = code.strip()
        
        return {"code": code}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate code: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3001,
        reload=True
    ) 