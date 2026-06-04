from app.database import supabase
from uuid import UUID

def calculate_stability_score(user_id: UUID):
    """Calculates the 0-100 Stability Score based on SRD Feature 1 metrics."""
    
    # 1. Fetch User Data
    user_res = supabase.table("users").select("monthly_income").eq("id", str(user_id)).execute()
    if not user_res.data:
        return {"error": "User not found"}
    
    income = user_res.data[0]["monthly_income"]
    if income <= 0:
        income = 1 # Prevent division by zero

    # 2. Fetch Buckets
    bucket_res = supabase.table("buckets").select("*").eq("user_id", str(user_id)).execute()
    if not bucket_res.data:
        return {"error": "Buckets not found"}
        
    bucket = bucket_res.data[0]
    buffer_amount = bucket["buffer_amount"]
    survival_amount = bucket["survival_amount"]

    # 3. Fetch Recent Transactions (Last 10) for Emotional Stress
    trans_res = supabase.table("transactions").select("emotion_tag").eq("user_id", str(user_id)).order("created_at", desc=True).limit(10).execute()
    transactions = trans_res.data

    # --- THE SCORING ALGORITHM (Total 100) ---
    score = 100
    
    # A. Emergency Readiness (30 points max)
    # Buffer should ideally be 20% of income
    buffer_ratio = buffer_amount / income
    if buffer_ratio < 0.10:
        score -= 20 # Critical: Less than 10% buffer
    elif buffer_ratio < 0.20:
        score -= 10 # Warning: Less than 20% buffer

    # B. Expense Pressure (30 points max)
    # If survival spending is > 80% of income, high pressure
    survival_ratio = survival_amount / income
    if survival_ratio > 0.80:
        score -= 20 # Critical: Spending too much on survival
    elif survival_ratio > 0.60:
        score -= 10 # Warning

    # C. Emotional Stress Signals (40 points max)
    # Count stress/panic tags in recent transactions
    stress_count = sum(1 for t in transactions if t.get("emotion_tag") in ["stress", "panic"])
    if stress_count >= 5:
        score -= 30 # High emotional toll
    elif stress_count >= 2:
        score -= 15 # Moderate emotional toll

    # Ensure score doesn't go below 0
    score = max(0, score)

    # --- DETERMINE STATUS LEVEL ---
    if score >= 75:
        status = "🟢 Stable"
    elif score >= 50:
        status = "🟡 Under Pressure"
    else:
        status = "🔴 High Stress Risk"

    return {
        "score": score,
        "status": status,
        "metrics": {
            "buffer_health": f"{int(buffer_ratio * 100)}%",
            "survival_pressure": f"{int(survival_ratio * 100)}%",
            "emotional_stress_events": stress_count
        }
    }

def generate_pressure_forecast(user_id: UUID):
    """Predicts future pressure based on recent spending patterns (SRD Feature 2)."""
    
    # Fetch recent categories to find recurring pressures
    trans_res = supabase.table("transactions").select("category", "description").eq("user_id", str(user_id)).order("created_at", desc=True).limit(20).execute()
    transactions = trans_res.data
    
    forecast = []
    
    # Simple AI/Rule-based forecasting (Hybrid approach)
    categories_seen = [t["category"].lower() for t in transactions]
    descriptions_seen = " ".join([t.get("description", "").lower() for t in transactions])
    
    if "school" in categories_seen or "school" in descriptions_seen:
        forecast.append("Week 3: School fee pressure approaching")
    if "transport" in categories_seen or "ride" in descriptions_seen:
        forecast.append("Week 4: Transport costs rising")
    if "food" in categories_seen or "groceries" in descriptions_seen:
        forecast.append("Week 2: Food inflation impact")
        
    # Fallback if no specific patterns found
    if not forecast:
        forecast.append("Week 3: General cost of living increase expected")
        forecast.append("Week 4: Buffer depletion risk if spending continues")

    return forecast