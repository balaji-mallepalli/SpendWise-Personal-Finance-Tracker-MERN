from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AlertCreate(BaseModel):
    budget_id: str
    threshold_pct: int = Field(default=90, ge=1, le=100)


class AlertResponse(BaseModel):
    id: str
    user_id: str
    budget_id: str
    threshold_pct: int
    triggered_at: Optional[str] = None
