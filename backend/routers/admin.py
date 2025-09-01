from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from ..database import Database
from ..deps import get_db_pool
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

class AgentBuilderReq(BaseModel):
    tenant_id: str = Field(..., description="Tenant UUID")
    name: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    system_prompt: str = Field(..., min_length=10)
    identity: Dict[str, Any] = Field(..., description="Agent identity configuration")
    mission: Dict[str, Any] = Field(..., description="Agent mission configuration")
    memory_mode: str = Field(..., pattern="^(thread|persistent)$", description="Memory mode: thread or persistent")

@router.post("/agent")
async def create_or_update_agent(req: AgentBuilderReq):
    """Create or update agent configuration with file storage"""
    
    # Get database instance
    pool = await get_db_pool()
    db = Database(pool)
    
    # Create storage directory for tenant
    storage_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "storage", req.tenant_id
    ))
    os.makedirs(storage_path, exist_ok=True)
    
    # Write identity.json and mission.json files
    try:
        with open(os.path.join(storage_path, "identity.json"), "w", encoding="utf-8") as f:
            json.dump(req.identity, f, indent=2, ensure_ascii=False)
        
        with open(os.path.join(storage_path, "mission.json"), "w", encoding="utf-8") as f:
            json.dump(req.mission, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        raise HTTPException(500, f"Failed to write agent files: {str(e)}")
    
    # Upsert agent in database
    agent = await db.upsert_agent(req.tenant_id, req.model_dump())
    
    return {
        "agent_id": agent["id"],
        "updated_at": datetime.utcnow().isoformat(),
        "storage_path": storage_path,
        "memory_mode": agent["memory_mode"]
    }

@router.get("/agent/{tenant_id}/{agent_name}")
async def get_agent(tenant_id: str, agent_name: str):
    """Get agent configuration"""
    pool = await get_db_pool()
    db = Database(pool)
    agent = await db.get_agent(tenant_id, agent_name)
    
    if not agent:
        raise HTTPException(404, "Agent not found")
    
    return {
        "id": agent["id"],
        "name": agent["name"],
        "avatar_url": agent["avatar_url"],
        "system_prompt": agent["system_prompt"],
        "identity": agent["identity_json"],
        "mission": agent["mission_json"],
        "memory_mode": agent["memory_mode"]
    }