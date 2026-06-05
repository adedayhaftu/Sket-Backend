from fastapi import APIRouter, HTTPException, Query
from uuid import UUID
from app.database import supabase
from app.services.stability_engine import calculate_stability_score, generate_pressure_forecast

router = APIRouter(
    prefix="/api/stability",
    tags=["Stability & Forecasting"]
)

@router.get("/{user_id}")
def get_stability_dashboard(user_id: UUID, lang: str = Query("en")):
    try:
        # 1. Calculate the Score (Feature 1) - Pass lang
        score_data = calculate_stability_score(user_id, lang=lang)
        
        # 2. Generate the Forecast (Feature 2) - Pass lang
        forecast = generate_pressure_forecast(user_id, lang=lang)
        
        # 3. Translate AI Insight
        status_word = score_data['status'].split(' ')[-1] if lang == "en" else score_data['status'].split(' ')[-1]
        if lang == "en":
            ai_insight = f"Your household is currently {status_word}. {forecast[0]}."
        else:
            ai_insight = f"ቤተሰብዎ በአሁኑ ጊዜ {status_word} ነው። {forecast[0]}."
        
        # 4. Combine into one dashboard response
        return {
            "user_id": str(user_id),
            "stability_score": score_data["score"],
            "status": score_data["status"],
            "metrics": score_data["metrics"],
            "pressure_forecast": forecast,
            "ai_insight": ai_insight
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/what-changed")
def what_changed(user_id: UUID, lang: str = Query("en")):
    """Enhanced: Explains what caused changes in the user's financial situation with structured timeline"""
    try:
        from app.database import supabase
        from datetime import datetime, timedelta
        
        # Fetch recent transactions (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        trans_res = supabase.table("transactions").select("*").eq("user_id", str(user_id)).gte("created_at", thirty_days_ago).order("created_at", desc=True).execute()
        transactions = trans_res.data or []
        
        # Fetch recent spikes
        spikes_res = supabase.table("spikes").select("*").eq("user_id", str(user_id)).order("created_at", desc=True).execute()
        spikes = spikes_res.data or []
        
        # Get user's monthly income for context
        user_res = supabase.table("users").select("monthly_income").eq("id", str(user_id)).execute()
        monthly_income = user_res.data[0]["monthly_income"] if user_res.data else 0
        
        timeline = []
        
        # Analyze spikes (these are major events)
        for spike in spikes[:3]:  # Top 3 recent spikes
            spike_date = datetime.fromisoformat(spike["created_at"].replace('Z', '+00:00'))
            week_number = 4 - ((datetime.now() - spike_date).days // 7)
            week_number = max(1, min(4, week_number))
            
            if lang == "en":
                timeline.append({
                    "week": week_number,
                    "title": f"Unexpected: {spike['title']}",
                    "description": f"{spike['amount']:,} ETB expense — absorbed by your Buffer.",
                    "type": "spike",
                    "amount": spike["amount"]
                })
            else:
                timeline.append({
                    "week": week_number,
                    "title": f"ያልተጠበቀ: {spike['title']}",
                    "description": f"{spike['amount']:,} ብር ወጪ — በማጠራቀሚያዎ ተሸክሟል።",
                    "type": "spike",
                    "amount": spike["amount"]
                })
        
        # Analyze transactions for patterns
        if len(transactions) >= 5:
            weeks = {}
            for trans in transactions:
                trans_date = datetime.fromisoformat(trans["created_at"].replace('Z', '+00:00'))
                week_num = 4 - ((datetime.now() - trans_date).days // 7)
                week_num = max(1, min(4, week_num))
                
                if week_num not in weeks:
                    weeks[week_num] = []
                weeks[week_num].append(trans)
            
            # Check for spending increases
            if len(weeks) >= 2:
                sorted_weeks = sorted(weeks.keys())
                recent_week = sorted_weeks[-1]
                previous_week = sorted_weeks[-2] if len(sorted_weeks) > 1 else None
                
                if previous_week:
                    recent_avg = sum(t["amount"] for t in weeks[recent_week]) / len(weeks[recent_week])
                    prev_avg = sum(t["amount"] for t in weeks[previous_week]) / len(weeks[previous_week])
                    
                    if recent_avg > prev_avg * 1.15:
                        increase_pct = int((recent_avg - prev_avg) / prev_avg * 100)
                        if lang == "en":
                            timeline.append({
                                "week": recent_week,
                                "title": f"Spending increased by {increase_pct}%",
                                "description": "Your average transaction size rose compared to previous week.",
                                "type": "cost_increase"
                            })
                        else:
                            timeline.append({
                                "week": recent_week,
                                "title": f"ወጪ በ{increase_pct}% ጨምሯል",
                                "description": "ከቀድሞው ሳምንት ጋር ሲነፃፀር አማካይ የወጪ መጠንዎ ጨምሯል።",
                                "type": "cost_increase"
                            })
            
            # Check for stress-driven spending
            stress_transactions = [t for t in transactions if t.get("emotion_tag") in ["stress", "panic"]]
            if len(stress_transactions) >= 2:
                if lang == "en":
                    timeline.append({
                        "week": 2,
                        "title": f"{len(stress_transactions)} stress-driven purchases",
                        "description": "Emotional spending detected — this is normal during pressure.",
                        "type": "emotional"
                    })
                else:
                    timeline.append({
                        "week": 2,
                        "title": f"{len(stress_transactions)} በጭንቀት የተነሳ ግዢዎች",
                        "description": "ስሜታዊ ወጪ ተገኝቷል — በጫና ወቅት ይህ የተለመደ ነው።",
                        "type": "emotional"
                    })
        
        # Add common external pressures (contextual)
        if len(timeline) < 4:
            if lang == "en":
                timeline.append({
                    "week": 1,
                    "title": "Transport costs rising",
                    "description": "Fuel prices increased in your area — affecting most households.",
                    "type": "external"
                })
            else:
                timeline.append({
                    "week": 1,
                    "title": "የትራንስፖርት ወጪዎች እየጨመሩ ነው",
                    "description": "በአካባቢዎ የነዳጅ ዋጋ ጨምሯል — አብዛኞቹን ቤተሰቦች ተጽዕኖ ፈጥሯል።",
                    "type": "external"
                })
        
        if len(timeline) < 4:
            if lang == "en":
                timeline.append({
                    "week": 4,
                    "title": "Food prices up 8%",
                    "description": "Regional supply shifts — you're not alone in feeling this.",
                    "type": "external"
                })
            else:
                timeline.append({
                    "week": 4,
                    "title": "የምግብ ዋጋ በ8% ጨምሯል",
                    "description": "የክልል አቅርቦት ለውጥ — ይህንን በመሰማት ብቻዎን አይደሉም።",
                    "type": "external"
                })
        
        # Sort by week
        timeline.sort(key=lambda x: x["week"])
        
        # Determine reassurance message
        spike_count = len([t for t in timeline if t["type"] == "spike"])
        external_count = len([t for t in timeline if t["type"] == "external"])
        
        if lang == "en":
            if spike_count > 0 and external_count > 0:
                reassurance = "Most of this month's pressure came from unexpected events and external cost increases — not personal mistakes. Be kind to yourself."
            elif spike_count > 0:
                reassurance = "You faced unexpected expenses this month. Your Buffer protected you. Take time to rebuild gently."
            elif external_count > 0:
                reassurance = "The environment changed around you. These external pressures affected everyone, not just you."
            else:
                reassurance = "Your spending pattern is stable. Keep up the good work!"
        else:
            if spike_count > 0 and external_count > 0:
                reassurance = "የዚህ ወር አብዛኛው ጫና ካልተጠበቁ ክስተቶች እና ከውጫዊ የወጪ ጭማሪዎች ነበር — ከግለሰባዊ ስህተቶች አይደለም። ራስዎን ይሩ።"
            elif spike_count > 0:
                reassurance = "በዚህ ወር ያልተጠበቁ ወጪዎች ገጥመውዎታል። ማጠራቀሚያዎ ጠብቆትዋል። በደንብ ለመገንባት ጊዜ ይውሰዱ።"
            elif external_count > 0:
                reassurance = "ዙሪያዎ ያለው አካባቢ ተቀይሯል። እነዚህ ውጫዊ ጫናዎች ሁሉንም ሰው ነው የነኩት፣ እርስዎን ብቻ አይደለም።"
            else:
                reassurance = "የወጪ ልማድዎ የተረጋጋ ነው። ጥሩ ስራዎን ይቀጥሉ!"
        
        return {
            "user_id": str(user_id),
            "timeline": timeline[:4],
            "reassurance": reassurance,
            "summary": f"Analyzed {len(transactions)} transactions and {len(spikes)} emergency events" if lang == "en" else f"{len(transactions)} ንግግሮች እና {len(spikes)} ድንገተኛ ክስተቶች ተተንትነዋል"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/adaptive-plan")
def generate_adaptive_plan(user_id: UUID, lang: str = Query("en")):
    try:
        score_data = calculate_stability_score(user_id, lang=lang)
        forecast = generate_pressure_forecast(user_id, lang=lang)
        
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

        # --- CALL THE AI TO GENERATE THE PLAN DYNAMICALLY - Pass lang! ---
        from app.services.gemini_ai import generate_survival_plan
        dynamic_plan = generate_survival_plan(
            income=monthly_income,
            survival=current_survival,
            joy=current_joy,
            buffer=current_buffer,
            threats=[primary_threat],
            stress_events=stress_events,
            language=lang  # <-- PASS THE LANGUAGE!
        )

        # AI Coaching Insight
        if lang == "en":
            if rearrangement_needed:
                ai_insight = (
                    f"Your current plan is failing to protect your Buffer (Deficit: {buffer_deficit} ETB). "
                    f"The AI has generated a unique {len(dynamic_plan)}-week strategy to recover from {primary_threat}."
                )
            else:
                ai_insight = "Your current plan is stable. The AI has generated an optimization strategy."
        else:
            if rearrangement_needed:
                ai_insight = (
                    f"የአሁኑ እቅድዎ ማጠራቀሚያዎን ለመጠበቅ አልቻለም (ጉድለት: {buffer_deficit} ብር)። "
                    f"AI ከ{primary_threat} ለማገገም ልዩ የ{len(dynamic_plan)}-ሳምንት ስልት ፈጥሯል።"
                )
            else:
                ai_insight = "የአሁኑ እቅድዎ የተረጋጋ ነው። AI የማመቻቸት ስልት ፈጥሯል።"

        return {
            "user_id": str(user_id),
            "current_status": score_data["status"],
            "trigger_reason": forecast[0] if forecast else ("Routine optimization" if lang == "en" else "የተለመደ ማመቻቸት"),
            "rearrangement_applied": rearrangement_needed,
            "buffer_deficit": buffer_deficit if rearrangement_needed else 0,
            "dynamic_4_week_plan": dynamic_plan,
            "ai_coaching": ai_insight
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))