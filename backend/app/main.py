"""
FastAPI application entrypoint.

Run with:  uvicorn app.main:app --reload
Docs at:   http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.database import Base, engine
from app.routers import auth, users, loans, financial, settlement, ai_letters

settings = get_settings()

# Create tables if they don't exist yet (fine for SQLite/dev; use Alembic
# migrations for production schema changes).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Debt Relief & Financial Recovery Platform",
    description=(
        "API for managing debt, analyzing financial health, predicting "
        "settlement outcomes, and generating AI-assisted negotiation strategies "
        "and letters."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(loans.router)
app.include_router(financial.router)
app.include_router(settlement.router)
app.include_router(ai_letters.router)


@app.get("/api/health", tags=["System"])
def health_check():
    return {"status": "ok"}
