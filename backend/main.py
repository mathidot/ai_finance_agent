# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio
import logging
from agent import finance_agent_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="Qwen Finance Agent API",
    description="API for interacting with the Qwen-powered financial assistant."
)

# CORS (Cross-Origin Resource Sharing) configuration
# This is crucial for allowing your frontend (running on a different port/origin)
# to make requests to your backend.
origins = [
    "http://localhost:8000",  # Default React/Vite development server port
    # Add other frontend origins if deployed, e.g., "https://your-frontend-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或 ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model for the chat endpoint
class ChatRequest(BaseModel):
    query: str

# Response model for the chat endpoint (optional, but good practice)
class ChatResponse(BaseModel):
    response: str
    error: Optional[str] = None

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Qwen Finance Agent API. Use /chat to interact."}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    if not finance_agent_service:
        raise HTTPException(status_code=503, detail="Finance Agent service is not initialized. Check backend logs for DASHSCOPE_API_KEY.")

    try:
        # Run the query using the agent service
        logging.info(f"Received query: {request.query}")
        agent_response = await finance_agent_service.run_query(request.query)
        return ChatResponse(response=agent_response)
    except Exception as e:
        # Log the error on the server
        print(f"Error in /chat endpoint: {e}")
        # Return a generic error to the frontend
        raise HTTPException(status_code=500, detail="Internal server error while processing your request.")

# Health check endpoint
@app.get("/health")
async def health_check():
    # You could add more sophisticated checks here, e.g., if LLM is reachable
    return {"status": "ok", "service": "Qwen Finance Agent API"}