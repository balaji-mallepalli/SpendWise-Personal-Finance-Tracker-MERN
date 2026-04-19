from pydantic import BaseModel, Field
from typing import Optional


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1)
    icon: str = Field(default="📁")
    color: str = Field(default="#6366f1")


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class CategoryResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    name: str
    icon: str
    color: str
