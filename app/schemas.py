"""Request/response models for the /query endpoint."""
from typing import Literal, Optional
from pydantic import BaseModel, Field

Confidence = Literal["High", "Medium", "Low"]
EscalationReason = Literal["sensitive_data", "low_confidence", "out_of_scope", "agent_error"]


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The customer's ticket / question.")
    category: Optional[str] = Field(
        None,
        description="Optional hint: billing | api | integrations | authentication | account | data.",
    )


class Citation(BaseModel):
    chunk_id: str
    doc: str
    score: float


class QueryResponse(BaseModel):
    answer: Optional[str] = None
    citations: list[Citation] = []
    confidence: Optional[Confidence] = None
    escalate: bool = False
    escalation_reason: Optional[EscalationReason] = None
