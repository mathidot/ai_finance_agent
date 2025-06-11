# backend/main.py
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json

# Import the agent service and callback handler
from agent import finance_agent_service
from callback_handler import ThinkingCallbackHandler

app = FastAPI(
    title="Qwen Finance Agent API",
    description="API for interacting with the Qwen-powered financial assistant."
)

# CORS (Cross-Origin Resource Sharing) configuration
# This is crucial for allowing your frontend (running on a different port/origin)
# to make requests to your backend.
origins = [
    "http://localhost:3000",  # Default React/Vite development server port
    # Add other frontend origins if deployed, e.g., "https://your-frontend-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Request body model for the chat endpoint
class ChatRequest(BaseModel):
    query: str

# Response model for the chat endpoint (optional, but good practice)
class ChatResponse(BaseModel):
    response: str
    error: Optional[str] = None
    thinking_process: Optional[List[str]] = None

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Qwen Finance Agent API. Use /chat to interact."}

@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    if not finance_agent_service:
        raise HTTPException(status_code=503, detail="Finance Agent service is not initialized. Check backend logs for DASHSCOPE_API_KEY.")

    try:
        # Run the query using the agent service
        agent_response = await finance_agent_service.run_query(request.query)
        return ChatResponse(response=agent_response)
    except Exception as e:
        # Log the error on the server
        print(f"Error in /chat endpoint: {e}")
        # Return a generic error to the frontend
        raise HTTPException(status_code=500, detail="Internal server error while processing your request.")

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    client_id = str(id(websocket))
    active_connections[client_id] = websocket
    
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            data_json = json.loads(data)
            
            if "query" in data_json:
                query = data_json["query"]
                
                # Create a callback handler for this specific websocket
                callback_handler = ThinkingCallbackHandler(websocket)
                
                try:
                    # Run the query with the callback handler
                    response = await finance_agent_service.run_query_with_thinking(
                        query, callback_handler
                    )
                    
                    # Send the final response
                    await websocket.send_json({
                        "type": "response",
                        "content": response,
                        "thinking_process": callback_handler.thinking_steps
                    })
                    
                except Exception as e:
                    print(f"Error processing websocket query: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "content": "Error processing your request."
                    })
    
    except WebSocketDisconnect:
        # Remove the connection when client disconnects
        if client_id in active_connections:
            del active_connections[client_id]
    except Exception as e:
        print(f"WebSocket error: {e}")
        # Remove the connection on error
        if client_id in active_connections:
            del active_connections[client_id]

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent_initialized": finance_agent_service is not None}

if __name__ == "__main__":
    import uvicorn
    print("Starting Qwen Finance Agent API server on http://localhost:3000")
    uvicorn.run(app, host="0.0.0.0", port=3000)