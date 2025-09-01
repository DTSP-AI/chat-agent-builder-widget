from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from ..database import Database
from ..deps import get_db_pool
from ..repo import push_to_ghl
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/leads", tags=["leads"])

class LeadIn(BaseModel):
    tenant_id: str = Field(..., description="Tenant UUID")
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    push_to_ghl: bool = Field(default=True, description="Whether to push lead to GoHighLevel")

class LeadOut(BaseModel):
    id: str
    tenant_id: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    notes: Optional[str]
    ghl_contact_id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

@router.post("", response_model=LeadOut)
async def create_or_update_lead(lead_data: LeadIn):
    """Create or update a lead, optionally pushing to GoHighLevel"""
    
    # Validate that we have at least email or phone
    if not lead_data.email and not lead_data.phone:
        raise HTTPException(400, "Either email or phone is required")
    
    # Get database instance
    pool = await get_db_pool()
    db = Database(pool)
    
    # Upsert lead in database
    lead = await db.upsert_lead(lead_data.tenant_id, lead_data.model_dump())
    
    # Push to GoHighLevel if requested
    ghl_contact_id = None
    if lead_data.push_to_ghl:
        try:
            ghl_contact_id = await push_to_ghl(lead)
            if ghl_contact_id:
                await db.update_lead_ghl_id(lead["id"], ghl_contact_id)
                lead["ghl_contact_id"] = ghl_contact_id
                logger.info(f"Lead {lead['id']} pushed to GHL: {ghl_contact_id}")
        except Exception as e:
            logger.error(f"Failed to push lead to GHL: {str(e)}")
            # Don't fail the request if GHL push fails
    
    return LeadOut(**lead)

@router.get("/{tenant_id}")
async def get_leads(tenant_id: str):
    """Get all leads for a tenant"""
    pool = await get_db_pool()
    db = Database(pool)
    
    leads = await db.get_leads_by_tenant(tenant_id)
    return [LeadOut(**lead) for lead in leads]