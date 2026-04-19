from pydantic import BaseModel, Field
from typing import Optional


class AccountCreate(BaseModel):
    name: str = Field(..., min_length=1)
    type: str = Field(..., pattern="^(bank|cash|credit|upi)$")
    balance: float = Field(default=0.0)


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = Field(default=None, pattern="^(bank|cash|credit|upi)$")
    balance: Optional[float] = None


class AccountResponse(BaseModel):
    id: str
    user_id: str
    name: str
    type: str
    balance: float
    created_at: str
