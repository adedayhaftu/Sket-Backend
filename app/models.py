from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

# --- User Models ---
class UserCreate(BaseModel):
    name: str
    email: Optional[str] = None
    monthly_income: Optional[float] = 0.0

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: Optional[str]
    monthly_income: float
    stability_score: float
    created_at: datetime

    class Config:
        from_attributes = True # Allows Pydantic to read from Supabase dictionaries

# --- Transaction Models ---
class TransactionCreate(BaseModel):
    user_id: UUID
    amount: float
    category: str
    emotion_tag: Optional[str] = None
    description: Optional[str] = None

# --- Spike Models ---
class SpikeCreate(BaseModel):
    user_id: UUID
    title: str
    amount: float
    description: Optional[str] = None