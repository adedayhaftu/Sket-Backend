from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models import UserCreate, UserResponse, UserUpdate
from uuid import UUID

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate):
    """Create a new user and initialize their buckets"""
    try:
        # 1. Create the user
        user_data = user.model_dump()
        response = supabase.table("users").insert(user_data).execute()
        created_user = response.data[0]
        
        # 2. Auto-create buckets based on income
        monthly_income = user.monthly_income
        
        # Calculate bucket allocations
        survival_amount = monthly_income * 0.51
        joy_amount = monthly_income * 0.08
        buffer_amount = monthly_income * 0.28
        
        # ✅ FIXED: Removed "monthly_income" since it doesn't exist in buckets table
        bucket_data = {
            "user_id": created_user["id"],
            "survival_amount": survival_amount,
            "joy_amount": joy_amount,
            "buffer_amount": buffer_amount,
            # Removed: "monthly_income": monthly_income,
        }
        
        supabase.table("buckets").insert(bucket_data).execute()
        
        return created_user
        
    except Exception as e:
        print(f"!!! BACKEND ERROR IN CREATE USER: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
# Get all users (for testing)
@router.get("/")
def get_users():
    try:
        response = supabase.table("users").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/email/{email}")
def get_user_by_email(email: str):
    """Get user by email address"""
    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
def get_user_by_id(user_id: UUID):
    """Get user by ID"""
    try:
        response = supabase.table("users").select("*").eq("id", str(user_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}")
def update_user(user_id: UUID, user: UserUpdate):
    """Update user profile"""
    try:
        update_data = user.model_dump(exclude_unset=True)
        response = supabase.table("users").update(update_data).eq("id", str(user_id)).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))