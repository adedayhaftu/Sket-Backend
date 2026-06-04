from fastapi import FastAPI
from app.database import test_connection

app = FastAPI(
    title="SUKET Backend API",
    description="AI Household Stress Stabilization Platform Backend",
    version="1.0.0"
)

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