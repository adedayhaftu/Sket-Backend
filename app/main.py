from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from app.database import test_connection
from app.routers import users, transactions, spikes, stability, buckets

app = FastAPI(
    title="SUKET Backend API",
    description="AI Household Stress Stabilization Platform Backend",
    version="1.0.0"
)

# BULLETPROOF CUSTOM CORS MIDDLEWARE
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    # 1. Handle preflight OPTIONS requests immediately
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "600"
        return response

    # 2. Process the actual request (GET, POST, etc.)
    response = await call_next(request)

    # 3. Add CORS headers to the response
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"

    return response

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
