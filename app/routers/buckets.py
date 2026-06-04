from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.database import supabase

router = APIRouter(prefix="/api/buckets", tags=["Buckets"])

@router.get("/{user_id}")
def get_user_buckets(user_id: UUID):
    """Get buckets for a specific user"""
    try:
        response = supabase.table("buckets").select("*").eq("user_id", str(user_id)).execute()
        if not response.data:
            # Return default buckets if none exist
            return {
                "survival_amount": 0,
                "joy_amount": 0,
                "buffer_amount": 0,
            }
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))