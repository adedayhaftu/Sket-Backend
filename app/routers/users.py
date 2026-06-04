from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models import UserCreate, UserResponse

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

# Create a new user
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate):
    try:
        # 1. Insert user into Supabase
        response = supabase.table("users").insert(user.dict()).execute()
        
        # 2. Automatically create a default bucket for this user
        user_id = response.data[0]['id']
        supabase.table("buckets").insert({
            "user_id": user_id,
            "survival_amount": 0,
            "joy_amount": 0,
            "buffer_amount": 0
        }).execute()
        
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all users (for testing)
@router.get("/")
def get_users():
    try:
        response = supabase.table("users").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))