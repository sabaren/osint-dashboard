"""WHOIS lookup service for domain registration info."""

import whois
from app.config import settings


class WhoisService:
    name = "whois"
    rate_limit = settings.WHOIS_RATE_LIMIT

    def query(self, domain: str) -> list[dict]:
        try:
            w = whois.whois(domain)
            if not w:
                return [{"type": "info", "value": "WHOIS returned no data"}]

            results = []

            if w.get("registrar"):
                results.append({"type": "registrar", "value": str(w["registrar"])})

            if w.get("creation_date"):
                dates = (
                    w["creation_date"]
                    if isinstance(w["creation_date"], list)
                    else [w["creation_date"]]
                )
                results.append({"type": "creation_date", "value": str(dates[0])})

            if w.get("expiration_date"):
                dates = (
                    w["expiration_date"]
                    if isinstance(w["expiration_date"], list)
                    else [w["expiration_date"]]
                )
                results.append({"type": "expiry_date", "value": str(dates[0])})

            if w.get("name_servers"):
                for ns in w["name_servers"]:
                    results.append({"type": "nameserver", "value": str(ns)})

            if w.get("org"):
                results.append({"type": "organization", "value": str(w["org"])})

            if w.get("country"):
                results.append({"type": "country", "value": str(w["country"])})

            # Extract emails from raw text if available
            if w.get("email"):
                emails = w["email"] if isinstance(w["email"], list) else [w["email"]]
                for email in emails:
                    results.append({"type": "email", "value": str(email)})

            return (
                results
                if results
                else [
                    {
                        "type": "info",
                        "value": "WHOIS data returned but no structured fields parsed",
                    }
                ]
            )
        except Exception as e:
            return [{"type": "error", "value": f"WHOIS lookup failed: {e}"}]
