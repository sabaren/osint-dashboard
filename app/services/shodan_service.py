"""Shodan API integration for open port and service discovery."""

import requests
from app.config import settings


class ShodanService:
    name = "shodan"
    rate_limit = settings.SHODAN_RATE_LIMIT  # req/min

    def query(self, domain: str) -> list[dict]:
        if not settings.SHODAN_API_KEY:
            return [{"type": "info", "value": "Shodan API key not configured"}]

        base_url = "https://api.shodan.io/shodan/host/search"
        params = {
            "query": domain,
            "key": settings.SHODAN_API_KEY,
            "limit": 20,
        }

        try:
            resp = requests.get(base_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()

            results = []
            for host in data.get("matches", []):
                for port in host.get("ports", []):
                    product = host.get("product", "unknown")
                    version = host.get("version", "")
                    results.append({
                        "type": "port",
                        "value": str(port),
                        "extra": f'{{"ip": "{host.get("ip_str", "")}", "product": "{product}", "version": "{version}"}}',
                    })
            return results
        except requests.RequestException as e:
            return [{"type": "error", "value": f"Shodan request failed: {e}"}]
