from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class AuditLogCreate(BaseModel):
    user_id: int
    action: str
    resource_type: str
    resource_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    resource_type: str
    resource_id: Optional[int]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

class AuditSummary(BaseModel):
    total_actions: int
    actions_by_type: Dict[str, int]
    actions_by_user: Dict[str, int]
    actions_by_resource: Dict[str, int]
    timeline: List[Dict[str, Any]]
    top_users: List[Dict[str, Any]]