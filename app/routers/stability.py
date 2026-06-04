from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.database import supabase
from app.services.stability_engine import calculate_stability_score, generate_pressure_forecast

router = APIRouter(
    prefix="/api/stability",
    tags=["Stability & Forecasting"]
)

@router.get("/{user_id}")
def get_stability_dashboard(user_id: UUID):
    try:
        # 1. Calculate the Score (Feature 1)
        score_data = calculate_stability_score(user_id)
        
        # 2. Generate the Forecast (Feature 2)
        forecast = generate_pressure_forecast(user_id)
        
        # 3. Combine into one dashboard response
        return {
            "user_id": str(user_id),
            "stability_score": score_data["score"],
            "status": score_data["status"],
            "metrics": score_data["metrics"],
            "pressure_forecast": forecast,
            "ai_insight": f"Your household is currently {score_data['status'].split(' ')[1]}. {forecast[0]}."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NEW: Feature 9 - What Changed?
@router.get("/{user_id}/what-changed")
def what_changed(user_id: UUID):
    """Explains what caused changes in the user's financial situation (SRD Feature 9)."""
    try:
        from app.database import supabase
        
        # Fetch recent transactions
        trans_res = supabase.table("transactions").select("*").eq("user_id", str(user_id)).order("created_at", desc=True).limit(20).execute()
        transactions = trans_res.data
        
        # Fetch recent spikes
        spikes_res = supabase.table("spikes").select("*").eq("user_id", str(user_id)).order("created_at", desc=True).limit(10).execute()
        spikes = spikes_res.data
        
        changes = []
        
        # Analyze spending increases
        if len(transactions) >= 5:
            recent_avg = sum(t["amount"] for t in transactions[:5]) / 5
            older_avg = sum(t["amount"] for t in transactions[5:10]) / len(transactions[5:10]) if len(transactions) > 5 else 0
            
            if recent_avg > older_avg * 1.2:  # 20% increase
                changes.append(f"Your average transaction size increased by {int((recent_avg - older_avg) / older_avg * 100)}%")
        
        # Check for stress-driven spending
        stress_transactions = [t for t in transactions if t.get("emotion_tag") in ["stress", "panic"]]
        if len(stress_transactions) >= 3:
            changes.append(f"You had {len(stress_transactions)} stress-driven purchases this period")
        
        # Check for emergencies
        if spikes:
            total_emergency = sum(s["amount"] for s in spikes)
            changes.append(f"Emergency expenses: {total_emergency} ETB from {len(spikes)} incident(s)")
        
        # If no specific changes found
        if not changes:
            changes.append("No significant changes detected. Your spending pattern is stable.")
        
        return {
            "user_id": str(user_id),
            "changes": changes,
            "summary": changes[0] if changes else "No changes",
            "reassurance": "You didn't fail. The environment changed. Let's adapt together."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/adaptive-plan")
def generate_adaptive_plan(user_id: UUID):
    try:
        score_data = calculate_stability_score(user_id)
        forecast = generate_pressure_forecast(user_id)
        
        bucket_res = supabase.table("buckets").select("*").eq("user_id", str(user_id)).execute()
        user_res = supabase.table("users").select("monthly_income").eq("id", str(user_id)).execute()
        
        if not bucket_res.data or not user_res.data:
            raise HTTPException(status_code=404, detail="User or Buckets not found")
            
        bucket = bucket_res.data[0]
        monthly_income = user_res.data[0]["monthly_income"]
        
        current_survival = bucket["survival_amount"]
        current_joy = bucket["joy_amount"]
        current_buffer = bucket["buffer_amount"]

        # Calculate deficit
        target_buffer = monthly_income * 0.20
        buffer_deficit = target_buffer - current_buffer
        rearrangement_needed = buffer_deficit > 0

        # Identify threats
        primary_threat = "general living costs"
        if any("school" in f.lower() for f in forecast): primary_threat = "school fees"
        elif any("transport" in f.lower() for f in forecast): primary_threat = "transport costs"
        elif any("food" in f.lower() for f in forecast): primary_threat = "food inflation"

        # Count recent stress events for the AI
        trans_res = supabase.table("transactions").select("emotion_tag").eq("user_id", str(user_id)).order("created_at", desc=True).limit(10).execute()
        stress_events = sum(1 for t in trans_res.data if t.get("emotion_tag") in ["stress", "panic"])

        # --- CALL THE AI TO GENERATE THE PLAN DYNAMICALLY ---
        from app.services.gemini_ai import generate_survival_plan
        dynamic_plan = generate_survival_plan(
            income=monthly_income,
            survival=current_survival,
            joy=current_joy,
            buffer=current_buffer,
            threats=[primary_threat],
            stress_events=stress_events
        )

        # AI Coaching Insight
        if rearrangement_needed:
            ai_insight = (
                f"Your current plan is failing to protect your Buffer (Deficit: {buffer_deficit} ETB). "
                f"The AI has generated a unique {len(dynamic_plan)}-week strategy to recover from {primary_threat}."
            )
        else:
            ai_insight = "Your current plan is stable. The AI has generated an optimization strategy."

        return {
            "user_id": str(user_id),
            "current_status": score_data["status"],
            "trigger_reason": forecast[0] if forecast else "Routine optimization",
            "rearrangement_applied": rearrangement_needed,
            "buffer_deficit": buffer_deficit if rearrangement_needed else 0,
            "dynamic_4_week_plan": dynamic_plan, # <--- THIS IS NOW 100% AI GENERATED!
            "ai_coaching": ai_insight
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))