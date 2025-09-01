from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import AnyMessage

class AgentState(TypedDict, total=False):
    tenant_id: str
    agent_id: str
    session_id: str
    input: str
    system_prompt: str
    history: List[AnyMessage]
    docs: List[str]  # from persistent memory retrieval (optional)
    response: str
    persist_memory: bool  # True => use pgvector pipeline
    notes_for_crm: Optional[str]
    identity: Dict[str, Any]
    mission: Dict[str, Any]