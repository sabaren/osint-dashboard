"""VirusTotal API integration for domain reputation and threat intel."""

import requests
from app.config import settings


class VirusTotalService:
    name = "virustotal"
    rate_limit = settings.VIRUSTOTAL_RATE_LIMIT

    def query(self, domain: str) -> list[dict]:
        if not settings.VIRUSTOTAL_API_KEY:
            return [{"type": "info", "value": "VirusTotal API key not configured"}]

        url = f"https://www.virustotal.com/api/v3/domains/{domain}"
        headers = {
            "x-apikey": settings.VIRUSTOTAL_API_KEY,
        }

        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            results = []
            attrs = data.get("data", {}).get("attributes", {})

            # Last analysis stats
            last_analysis = attrs.get("last_analysis_stats", {})
            results.append(
                {
                    "type": "threat_stats",
                    "value": f"Malicious: {last_analysis.get('malicious', 0)}, "
                    f"Suspicious: {last_analysis.get('suspicious', 0)}, "
                    f"Undetected: {last_analysis.get('undetected', 0)}, "
                    f"Harmless: {last_analysis.get('harmless', 0)}",
                }
            )

            # Last analysis results
            for engine, result in attrs.get("last_analysis_results", {}).items():
                category = result.get("category", "")
                if category in ("malicious", "suspicious"):
                    method = result.get("result", "")
                    results.append(
                        {
                            "type": "threat",
                            "value": f"{engine}: {category} ({method})",
                        }
                    )

            # Reputation
            reputation = attrs.get("reputation", "N/A")
            results.append({"type": "reputation", "value": str(reputation)})

            # Categories
            for source, cat in attrs.get("last_analysis_results", {}).items():
                if cat.get("category"):
                    results.append(
                        {
                            "type": "category",
                            "value": f"{source}: {cat['category']}",
                        }
                    )

            return results
        except requests.RequestException as e:
            return [{"type": "error", "value": f"VirusTotal request failed: {e}"}]
