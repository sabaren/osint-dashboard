"""Dashboard UI routes."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Scan

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_session)):
    """Main dashboard page."""
    recent_scans = db.query(Scan).order_by(Scan.created_at.desc()).limit(10).all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "scans": recent_scans,
    })


@router.get("/scan/{scan_id}", response_class=HTMLResponse)
def scan_results(request: Request, scan_id: int, db: Session = Depends(get_session)):
    """Detailed results for a single scan."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "scans": [],
            "error": "Scan not found",
        })

    # Aggregate stats
    results_by_source = {}
    results_by_type = {}
    for r in scan.results:
        results_by_source[r.source] = results_by_source.get(r.source, 0) + 1
        results_by_type[r.data_type] = results_by_type.get(r.data_type, 0) + 1

    return templates.TemplateResponse("scan_results.html", {
        "request": request,
        "scan": scan,
        "results": scan.results,
        "results_by_source": results_by_source,
        "results_by_type": results_by_type,
    })


@router.get("/batch", response_class=HTMLResponse)
def batch_page(request: Request):
    """Batch scan page."""
    return templates.TemplateResponse("batch.html", {
        "request": request,
    })
