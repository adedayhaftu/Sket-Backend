from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

# --- User Models ---
class UserCreate(BaseModel):
    name: str
    email: Optional[str] = None
    monthly_income: Optional[float] = 0.0
    # NEW FIELDS
    monthly_rent: Optional[float] = 0.0
    monthly_transport: Optional[float] = 0.0
    monthly_school_fees: Optional[float] = 0.0
    dependents: Optional[int] = 0
    city: Optional[str] = "Addis Ababa"

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: Optional[str]
    monthly_income: float
    # NEW FIELDS
    monthly_rent: Optional[float]
    monthly_transport: Optional[float]
    monthly_school_fees: Optional[float]
    dependents: Optional[int]
    city: Optional[str]
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

# --- User Update Model ---
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    monthly_income: Optional[float] = None
    # NEW FIELDS
    monthly_rent: Optional[float] = None
    monthly_transport: Optional[float] = None
    monthly_school_fees: Optional[float] = None
    dependents: Optional[int] = None
    city: Optional[str] = None