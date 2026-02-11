from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.orchestration.graph import MultiAgentOrchestrator
from src.config import Config

app = FastAPI(title="Customer Support Multi-Agent MCP Server", version="1.0.0")

orchestrator = None

class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Dict[str, str]]] = None

class QueryResponse(BaseModel):
    response: str
    success: bool
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup"""
    global orchestrator
    try:
        Config.validate()
        orchestrator = MultiAgentOrchestrator()
        print("Multi-agent orchestrator initialized successfully")
    except Exception as e:
        print(f"Error initializing orchestrator: {e}")
        raise

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Customer Support Multi-Agent System",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "orchestrator": "initialized" if orchestrator else "not initialized"
    }

@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """Handle user query through multi-agent system"""
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        response = orchestrator.query(
            request.query,
            request.conversation_history
        )
        
        return QueryResponse(
            response=response,
            success=True,
            error=None
        )
    
    except Exception as e:
        return QueryResponse(
            response="",
            success=False,
            error=str(e)
        )

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        sql_stats = orchestrator.sql_agent.get_database_stats()
        vector_stats = orchestrator.rag_agent.vector_store.get_collection_stats()
        
        return {
            "database": sql_stats,
            "vector_store": vector_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
