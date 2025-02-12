from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from hyperpocket_openai import PocketOpenAI
from openai import OpenAI
from tools import send_mail, take_a_picture, call_diffusion_model
import os

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_model():
    global pocket, llm, tool_specs, tools

    if pocket:
        pocket._teardown_server()

    tools = {
        send_mail.name: {"tool": send_mail},
        take_a_picture.name: {"tool": take_a_picture},
        call_diffusion_model.name: {"tool": call_diffusion_model},
    }
    tool_list = [tool["tool"] for tool in tools.values()]
    pocket = PocketOpenAI(tools=tool_list)
    tool_specs = pocket.get_open_ai_tool_specs()
    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        if not request.prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response: ChatCompletion = llm.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tool_specs,
            )

        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": request.prompt}]
        )

        response = completion.choices[0].message.content
        return {"response": response}

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=3001, reload=True) 