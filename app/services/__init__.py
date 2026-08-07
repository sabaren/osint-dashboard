"""Service layer for OSINT data sources."""

import time
from app.config import settings
from app.services.shodan_service import ShodanService
from app.services.crt_service import CRTService
from app.services.whois_service import WhoisService
from app.services.virustotal_service import VirusTotalService
from app.services.dns_service import DNSService

ALL_SERVICES = [ShodanService, CRTService, WhoisService, VirusTotalService, DNSService]
SERVICE_ENABLED = {
    "shodan": settings.SHODAN_ENABLED,
    "crt_sh": settings.CRT_ENABLED,
    "whois": settings.WHOIS_ENABLED,
    "virustotal": settings.VIRUSTOTAL_ENABLED,
    "dns": settings.DNS_ENABLED,
}


def get_active_services() -> list:
    """Return list of enabled service classes."""
    return [svc for svc in ALL_SERVICES if SERVICE_ENABLED.get(svc.name, True)]


def run_scan_for_domain(scan_id: int, domain: str, recursive: bool, db, celery_task):
    """Run all data sources against a domain, store results, optionally recurse."""
    from app.models import ScanResult
    from app.database import SessionLocal

    active_services = get_active_services()
    total_services = len(active_services)
    current = 0
    subdomains_found = set()

    for svc_class in active_services:
        svc = svc_class()
        try:
            results = svc.query(domain)
            for res in results:
                record = ScanResult(
                    scan_id=scan_id,
                    source=svc.name,
                    target=domain,
                    data_type=res.get("type", "unknown"),
                    value=res.get("value", ""),
                    extra=res.get("extra", "{}"),
                )
                db.add(record)
                if res.get("type") == "subdomain":
                    subdomains_found.add(res["value"])

            if recursive and subdomains_found:
                for sub in list(subdomains_found)[:settings.MAX_RECURSIVE_TARGETS]:
                    sub_db = SessionLocal()
                    try:
                        sub_results = svc.query(sub)
                        for res in sub_results:
                            record = ScanResult(
                                scan_id=scan_id,
                                source=svc.name,
                                target=sub,
                                data_type=res.get("type", "unknown"),
                                value=res.get("value", ""),
                                extra=res.get("extra", "{}"),
                            )
                            sub_db.add(record)
                    finally:
                        sub_db.commit()
                        sub_db.close()

            db.commit()

            # Rate limit: sleep between API calls
            current += 1
            celery_task.update_state(
                state="PROGRESS",
                meta={"current": current, "total": total_services, "domain": domain}
            )
            time.sleep(60 / svc.rate_limit)

        except Exception as e:
            print(f"[ERROR] {svc.name} failed for {domain}: {e}")
            db.rollback()
            current += 1
            celery_task.update_state(
                state="PROGRESS",
                meta={"current": current, "total": total_services, "domain": domain, "error": str(e)}
            )
