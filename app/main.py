from fastapi import FastAPI
from app.database import test_connection
from app.routers import users

# Initialize the FastAPI app
app = FastAPI(
    title="SUKET Backend API",
    description="AI Household Stress Stabilization Platform Backend",
    version="1.0.0"
)

# Include the users router
app.include_router(users.router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to SUKET Backend API",
        "status": "Running smoothly 🟢",
        "tagline": "Protecting Your Peace During Uncertain Times."
    }

# Database connection check endpoint
@app.get("/api/db-check")
def check_database():
    return test_connection()