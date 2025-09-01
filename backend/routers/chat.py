from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from ..database import Database
from ..deps import get_db_pool
from ..agents.graph import compile_graph
from ..agents.state import AgentState
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Compile the graph once at module level
graph = compile_graph()

class ChatIn(BaseModel):
    tenant_id: str = Field(..., description="Tenant UUID")
    agent_name: str = Field(..., description="Agent name")
    session_id: str = Field(..., description="Client session ID")
    user_input: str = Field(..., max_length=1000, description="User message")

class ChatOut(BaseModel):
    reply: str
    notes_for_crm: Optional[str] = None
    agent_id: str
    session_id: str

@router.post("", response_model=ChatOut)
async def chat(req: ChatIn):
    """Process chat message through LangGraph agent"""
    
    # Get database instance
    pool = await get_db_pool()
    db = Database(pool)
    
    # Get agent for tenant
    agent = await db.get_agent(req.tenant_id, req.agent_name)
    if not agent:
        raise HTTPException(404, f"Agent '{req.agent_name}' not found for tenant {req.tenant_id}")
    
    # Prepare agent state
    state: AgentState = {
        "tenant_id": req.tenant_id,
        "agent_id": agent["id"],
        "session_id": req.session_id,
        "input": req.user_input,
        "system_prompt": agent["system_prompt"],
        "persist_memory": agent["memory_mode"] == "persistent",
        "identity": agent["identity_json"],
        "mission": agent["mission_json"],
        "history": [],  # Handled by RunnableWithMessageHistory
        "docs": []
    }
    
    try:
        # Run the graph
        result = graph.invoke(state, config={
            "configurable": {
                "session_id": f"{req.tenant_id}:{agent['id']}:{req.session_id}"
            }
        })
        
        logger.info(f"Chat processed for session {req.session_id}")
        
        return ChatOut(
            reply=result["response"],
            notes_for_crm=result.get("notes_for_crm"),
            agent_id=agent["id"],
            session_id=req.session_id
        )
        
    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}")
        raise HTTPException(500, f"Chat processing failed: {str(e)}")