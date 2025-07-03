from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.agent.agent_core import get_agent_response

app = FastAPI(title="Calendar Booking AI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "BookBuddy Backend is running!"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_message = request.message
    response = await get_agent_response(user_message)
    return ChatResponse(reply=response)
