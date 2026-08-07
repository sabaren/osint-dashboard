"""Scan management routes."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_session
from app.models import Scan
from app.celery_app import scan_domain

router = APIRouter(prefix="/api/scans", tags=["scans"])


class ScanRequest(BaseModel):
    domain: str
    recursive: bool = False


class BatchScanRequest(BaseModel):
    domains: list[str]
    recursive: bool = False


@router.post("/")
async def create_scan(
    domain: str = Form(None),
    sources: Optional[str] = Form(None),
    recursive: bool = Form(False),
    include_subdomains: bool = Form(False),
    background: BackgroundTasks = None,
    db: Session = Depends(get_session),
):
    """Start a new scan for a domain."""
    if not domain or not domain.strip():
        raise HTTPException(status_code=400, detail="Domain is required")

    domain = domain.strip()

    existing = db.query(Scan).filter(
        Scan.domain == domain,
        Scan.status.in_(["pending", "running"])
    ).first()

    if existing:
        return {"id": existing.id, "status": existing.status, "domain": existing.domain}

    scan = Scan(domain=domain, status="pending")
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Queue the scan task
    scan_domain.delay(domain, recursive)

    return {"id": scan.id, "status": scan.status, "domain": scan.domain}


@router.post("/batch")
async def batch_scan(
    domains: str = Form(None),
    recursive: bool = Form(False),
    db: Session = Depends(get_session),
):
    """Start scans for multiple domains."""
    if not domains:
        raise HTTPException(status_code=400, detail="Domains are required")

    domain_list = [d.strip() for d in domains.split("\n") if d.strip()]
    results = []
    for domain in domain_list:
        existing = db.query(Scan).filter(
            Scan.domain == domain,
            Scan.status.in_(["pending", "running"])
        ).first()

        if existing:
            results.append({"domain": domain, "id": existing.id, "status": existing.status})
        else:
            scan = Scan(domain=domain, status="pending")
            db.add(scan)
            db.commit()
            db.refresh(scan)
            scan_domain.delay(domain, recursive)
            results.append({"domain": domain, "id": scan.id, "status": scan.status})

    return results


@router.get("/")
def list_scans(limit: int = 20, db: Session = Depends(get_session)):
    """List recent scans."""
    scans = db.query(Scan).order_by(Scan.created_at.desc()).limit(limit).all()
    return [
        {
            "id": s.id,
            "domain": s.domain,
            "status": s.status,
            "created_at": str(s.created_at),
            "result_count": len(s.results),
        }
        for s in scans
    ]


@router.get("/{scan_id}")
def get_scan(scan_id: int, db: Session = Depends(get_session)):
    """Get scan details with results."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return {
        "id": scan.id,
        "domain": scan.domain,
        "status": scan.status,
        "created_at": str(scan.created_at),
        "results": [
            {
                "id": r.id,
                "source": r.source,
                "target": r.target,
                "data_type": r.data_type,
                "value": r.value,
                "extra": r.extra,
                "detected_at": str(r.detected_at),
            }
            for r in scan.results
        ],
    }
