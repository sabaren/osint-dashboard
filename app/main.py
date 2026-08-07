"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import engine, Base
from app.config import settings
from app.routers import scans
from app.routers.dashboard import router as dashboard_router
from app.routers.export import router as export_router

os.makedirs("app/static", exist_ok=True)
os.makedirs("app/templates", exist_ok=True)
os.makedirs("data", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown


app = FastAPI(
    title="OSINT Dashboard",
    description="Web-based threat intelligence platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routers
app.include_router(scans.router)
app.include_router(dashboard_router)
app.include_router(export_router)


@app.get("/health")
def health_check():
    """Health endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "celery_broker": settings.CELERY_BROKER_URL,
    }
