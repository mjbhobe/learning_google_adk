from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class AgentRequest(BaseModel):
    payload: Dict[str, Any] = Field(default_factory=dict)
    prompt: Optional[str] = None


class AgentResponse(BaseModel):
    status: str = "ok"
    result: str
    meta: Dict[str, Any] = Field(default_factory=dict)
