from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models import SpikeCreate

router = APIRouter(
    prefix="/api/spikes",
    tags=["Spikes (Emergencies)"]
)

@router.post("/")
def log_spike(spike: SpikeCreate):
    try:
        # 1. Insert Spike
        spike_data = {
            "user_id": str(spike.user_id),
            "title": spike.title,
            "amount": spike.amount,
            "description": spike.description
        }
        supabase.table("spikes").insert(spike_data).execute()

        # 2. Drain the Buffer (SRD Feature 6)
        bucket_res = supabase.table("buckets").select("buffer_amount").eq("user_id", str(spike.user_id)).execute()
        if bucket_res.data:
            current_buffer = bucket_res.data[0]["buffer_amount"]
            new_buffer = max(0, current_buffer - spike.amount)
            
            supabase.table("buckets").update({"buffer_amount": new_buffer}).eq("user_id", str(spike.user_id)).execute()
            
            return {
                "message": f"Spike '{spike.title}' logged. Buffer protected you!",
                "new_buffer_balance": new_buffer
            }
        return {"message": "Spike logged, but no bucket found."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))