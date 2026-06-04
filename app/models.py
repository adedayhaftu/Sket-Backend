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
        from_attributes = True

# --- Transaction Models (Feature 3 & 7) ---
class TransactionCreate(BaseModel):
    user_id: UUID
    amount: float
    category: str # e.g., "food", "transport", "coffee"
    description: Optional[str] = None

class TransactionResponse(BaseModel):
    id: UUID
    user_id: UUID
    amount: float
    category: str
    emotion_tag: Optional[str] # AI will fill this!
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# --- Spike Models (Feature 6) ---
class SpikeCreate(BaseModel):
    user_id: UUID
    title: str # e.g., "Toothache"
    amount: float
    description: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    monthly_income: Optional[float] = None