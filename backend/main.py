"""
Noesis Backend
FastAPI server for the Creative Philosophy Studio
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.config import engine, Base
from routes import documents, blocks, ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for the application"""
    # Startup: Create database tables
    async with engine.begin() as conn:
        # In production, use Alembic migrations instead
        await conn.run_sync(Base.metadata.create_all)
    
    print("🚀 Noesis backend started")
    print("📚 Database tables created")
    print("🧠 LLM service initialized")
    
    yield
    
    # Shutdown
    await engine.dispose()
    print("👋 Noesis backend shutdown")


# Create FastAPI app
app = FastAPI(
    title="Noesis API",
    description="The Creative Philosophy Studio - API for rigorous intellectual creation",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for Next.js frontend
# Get allowed origins from environment variable or use defaults
import os
cors_origins_env = os.getenv("CORS_ORIGINS", "")
additional_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",  # Alternative port
] + additional_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api")
app.include_router(blocks.router, prefix="/api")
app.include_router(ai.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Noesis API",
        "tagline": "The Creative Philosophy Studio",
        "philosophy": "Writing as Thinking. Every paragraph is a malleable object with infinite versions.",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "noesis-backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


