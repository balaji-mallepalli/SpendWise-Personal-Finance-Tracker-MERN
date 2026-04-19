from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TransactionCreate(BaseModel):
    account_id: str
    category_id: str
    amount: float = Field(..., gt=0)
    type: str = Field(..., pattern="^(income|expense)$")
    description: str = Field(default="")
    date: datetime


class TransactionUpdate(BaseModel):
    account_id: Optional[str] = None
    category_id: Optional[str] = None
    amount: Optional[float] = Field(default=None, gt=0)
    type: Optional[str] = Field(default=None, pattern="^(income|expense)$")
    description: Optional[str] = None
    date: Optional[datetime] = None


class TransactionResponse(BaseModel):
    id: str
    user_id: str
    account_id: str
    category_id: str
    amount: float
    type: str
    description: str
    date: str
    created_at: str


class TransactionFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category_id: Optional[str] = None
    type: Optional[str] = None
    account_id: Optional[str] = None
