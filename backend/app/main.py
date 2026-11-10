"""FastAPI entry point for the PMFBY Crop Analytics service.

- CORS is wide‑open for local development (adjust in production).
- Routers are registered lazily; they will be added in later phases.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .config import settings

app = FastAPI(title="PMFBY Crop Analytics API", version="0.1.0")

# CORS – allow any origin during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Register API routers
from .routers import analytics, claims, reports
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(claims.router, prefix="/claims", tags=["Claims"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])

# -------------------------------------------------------------------
# Create database tables on startup (development convenience)
from .database import Base, engine
Base.metadata.create_all(bind=engine)

# Serve Frontend directly from FastAPI if available
frontend_dir = Path(__file__).resolve().parent.parent.parent / "Frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")



