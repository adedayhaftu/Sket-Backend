from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import test_connection
from app.routers import users, transactions, spikes, stability, buckets

app = FastAPI(
    title="SUKET Backend API",
    description="AI Household Stress Stabilization Platform Backend",
    version="1.0.0"
)

# CORS Configuration - Allow your Vercel domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://sket-frontend-7fjy-702jejdid-hewan-meharis-projects.vercel.app",
        "https://sket-frontend.vercel.app",
        "https://*.vercel.app",  # Allow all Vercel preview URLs
    ],
    allow_credentials=True,  # Can be True now since we're listing specific domains
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
async def root():
    return {
        "message": "SUKET Backend API is running",
        "status": "healthy",
        "cors": "enabled"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Include routers
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(spikes.router)
app.include_router(stability.router)
app.include_router(buckets.router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )
