from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models import TransactionCreate, TransactionResponse
from app.services.gemini_ai import analyze_emotion

router = APIRouter(
    prefix="/api/transactions",
    tags=["Transactions"]
)

@router.post("/", response_model=TransactionResponse)
def log_transaction(transaction: TransactionCreate):
    try:
        # 1. AI Emotion Detection (SRD Feature 7)
        emotion_tag = analyze_emotion(transaction.description, transaction.category)

        # 2. Insert Transaction into DB
        trans_data = {
            "user_id": str(transaction.user_id),
            "amount": transaction.amount,
            "category": transaction.category,
            "emotion_tag": emotion_tag,
            "description": transaction.description
        }
        trans_response = supabase.table("transactions").insert(trans_data).execute()

        # 3. Update Wellness Buckets (SRD Feature 3)
        # Logic: Deduct from Survival, Joy, or Buffer based on category
        bucket_to_update = "survival_amount"
        if transaction.category.lower() in ["coffee", "entertainment", "social", "joy"]:
            bucket_to_update = "joy_amount"
        elif transaction.category.lower() in ["emergency", "health", "buffer"]:
            bucket_to_update = "buffer_amount"

        # Fetch current bucket
        bucket_res = supabase.table("buckets").select("*").eq("user_id", str(transaction.user_id)).execute()
        if bucket_res.data:
            current_amount = bucket_res.data[0][bucket_to_update]
            new_amount = max(0, current_amount - transaction.amount) # Prevent negative
            
            supabase.table("buckets").update({bucket_to_update: new_amount}).eq("user_id", str(transaction.user_id)).execute()

        return trans_response.data[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))