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

# CORS Configuration - MUST BE FIRST
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow ALL domains
    allow_credentials=False,  # MUST BE FALSE when using "*"
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Handle ALL OPTIONS requests BEFORE routers
@app.api_route("/{path:path}", methods=["OPTIONS"])
async def options_handler(request: Request, path: str):
    return Response(status_code=200)

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

# Include routers AFTER CORS and OPTIONS handler
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
