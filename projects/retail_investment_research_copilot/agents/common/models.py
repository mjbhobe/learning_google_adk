from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Request model shared by all agent services."""

    payload: Dict[str, Any] = Field(default_factory=dict)
    prompt: Optional[str] = None


class AgentResponse(BaseModel):
    """Response model shared by all agent services."""

    status: str = "ok"
    result: str
    meta: Dict[str, Any] = Field(default_factory=dict)
