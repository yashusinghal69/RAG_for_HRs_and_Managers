from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import os
from graph import run_workflow

app = FastAPI(title="RAG Workflow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://*.vercel.app",  # Allow all Vercel subdomains
        "https://vercel.app",     # Vercel root domain
        "*"  # Allow all origins (remove this in production for security)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WorkflowRequest(BaseModel):
    query: str
    user_id: str

class WorkflowResponse(BaseModel):
    success: bool
    data: Dict[str, Any] = None
    error: str = None

@app.post("/api/workflow", response_model=WorkflowResponse)
async def process_workflow(request: WorkflowRequest):
   
    try:
        print(f"Received request - Query: {request.query}, User ID: {request.user_id}")
        
        result = run_workflow(request.query, request.user_id)
        
        return WorkflowResponse(
            success=True,
            data=result
        )
    except Exception as e:
        print(f"Error processing workflow: {str(e)}")
        return WorkflowResponse(
            success=False,
            error=str(e)
        )

if __name__ == "__main__":
    
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=False)
    # uvicorn api_server:app --host 0.0.0.0 --port 8000