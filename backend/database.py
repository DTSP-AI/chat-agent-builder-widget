import asyncpg
import os
import logging
from typing import Optional, Dict, Any, List
import json
import uuid

logger = logging.getLogger(__name__)

class Database:
    """Direct PostgreSQL database operations using asyncpg"""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def execute_migration(self, migration_sql: str) -> None:
        """Execute database migration"""
        async with self.pool.acquire() as conn:
            await conn.execute(migration_sql)
            logger.info("Migration executed successfully")
    
    async def ensure_tenant(self, tenant_id: str, name: str = None) -> Dict[str, Any]:
        """Ensure tenant exists"""
        async with self.pool.acquire() as conn:
            tenant = await conn.fetchrow("SELECT * FROM tenants WHERE id = $1", tenant_id)
            if not tenant:
                await conn.execute(
                    "INSERT INTO tenants (id, name) VALUES ($1, $2)",
                    tenant_id, name or f"Tenant {tenant_id}"
                )
                tenant = await conn.fetchrow("SELECT * FROM tenants WHERE id = $1", tenant_id)
            return dict(tenant)
    
    async def get_agent(self, tenant_id: str, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent by tenant and name"""
        async with self.pool.acquire() as conn:
            agent = await conn.fetchrow(
                "SELECT * FROM agents WHERE tenant_id = $1 AND name = $2",
                tenant_id, agent_name
            )
            if agent:
                result = dict(agent)
                # Parse JSON fields
                result["identity_json"] = json.loads(agent["identity_json"]) if agent["identity_json"] else {}
                result["mission_json"] = json.loads(agent["mission_json"]) if agent["mission_json"] else {}
                return result
            return None
    
    async def upsert_agent(self, tenant_id: str, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update agent"""
        async with self.pool.acquire() as conn:
            # Ensure tenant exists
            await self.ensure_tenant(tenant_id)
            
            existing = await conn.fetchrow(
                "SELECT * FROM agents WHERE tenant_id = $1 AND name = $2",
                tenant_id, agent_data["name"]
            )
            
            if existing:
                # Update
                await conn.execute("""
                    UPDATE agents 
                    SET avatar_url = $3, system_prompt = $4, identity_json = $5, 
                        mission_json = $6, memory_mode = $7, updated_at = NOW()
                    WHERE tenant_id = $1 AND name = $2
                """, tenant_id, agent_data["name"], agent_data.get("avatar_url"),
                    agent_data["system_prompt"], json.dumps(agent_data["identity"]),
                    json.dumps(agent_data["mission"]), agent_data["memory_mode"])
                
                agent = await conn.fetchrow(
                    "SELECT * FROM agents WHERE tenant_id = $1 AND name = $2",
                    tenant_id, agent_data["name"]
                )
            else:
                # Create
                agent_id = str(uuid.uuid4())
                await conn.execute("""
                    INSERT INTO agents (id, tenant_id, name, avatar_url, system_prompt, 
                                      identity_json, mission_json, memory_mode)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, agent_id, tenant_id, agent_data["name"], agent_data.get("avatar_url"),
                    agent_data["system_prompt"], json.dumps(agent_data["identity"]),
                    json.dumps(agent_data["mission"]), agent_data["memory_mode"])
                
                agent = await conn.fetchrow("SELECT * FROM agents WHERE id = $1", agent_id)
            
            result = dict(agent)
            result["identity_json"] = json.loads(agent["identity_json"]) if agent["identity_json"] else {}
            result["mission_json"] = json.loads(agent["mission_json"]) if agent["mission_json"] else {}
            return result
    
    async def upsert_lead(self, tenant_id: str, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update lead"""
        async with self.pool.acquire() as conn:
            email = lead_data.get("email")
            
            # Find existing by email
            lead = None
            if email:
                lead = await conn.fetchrow(
                    "SELECT * FROM leads WHERE tenant_id = $1 AND email = $2",
                    tenant_id, email
                )
            
            if not lead:
                # Create
                lead_id = str(uuid.uuid4())
                await conn.execute("""
                    INSERT INTO leads (id, tenant_id, first_name, last_name, email, phone, notes)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, lead_id, tenant_id, 
                    lead_data.get("first_name"), lead_data.get("last_name"),
                    lead_data.get("email"), lead_data.get("phone"), lead_data.get("notes"))
                
                lead = await conn.fetchrow("SELECT * FROM leads WHERE id = $1", lead_id)
            else:
                # Update
                await conn.execute("""
                    UPDATE leads 
                    SET first_name = $3, last_name = $4, email = $5, phone = $6, notes = $7, updated_at = NOW()
                    WHERE id = $1 AND tenant_id = $2
                """, lead["id"], tenant_id,
                    lead_data.get("first_name"), lead_data.get("last_name"),
                    lead_data.get("email"), lead_data.get("phone"), lead_data.get("notes"))
                
                lead = await conn.fetchrow("SELECT * FROM leads WHERE id = $1", lead["id"])
            
            return dict(lead)
    
    async def update_lead_ghl_id(self, lead_id: str, ghl_contact_id: str) -> None:
        """Update lead with GHL contact ID"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "UPDATE leads SET ghl_contact_id = $1 WHERE id = $2",
                ghl_contact_id, lead_id
            )
    
    async def get_leads_by_tenant(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get all leads for tenant"""
        async with self.pool.acquire() as conn:
            leads = await conn.fetch(
                "SELECT * FROM leads WHERE tenant_id = $1 ORDER BY created_at DESC",
                tenant_id
            )
            return [dict(lead) for lead in leads]