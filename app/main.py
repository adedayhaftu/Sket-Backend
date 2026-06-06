from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import test_connection
from app.routers import users, transactions, spikes, stability, buckets 

app = FastAPI(
    title="SUKET Backend API",
    description="AI Household Stress Stabilization Platform Backend",
    version="1.0.0"
)

# ✅ FIXED CORS: When using "*", credentials MUST be False.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains (perfect for hackathon)
    allow_credentials=False, # MUST BE FALSE WHEN ORIGINS IS "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(spikes.router)
app.include_router(stability.router) 
app.include_router(buckets.router) 

@app.get("/")
def read_root():
    return {
        "message": "Welcome to SUKET Backend API",
        "status": "Running smoothly 🟢",
        "tagline": "Protecting Your Peace During Uncertain Times."
    }

@app.get("/api/db-check")
def check_database():
    return test_connection()
