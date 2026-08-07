"""CRT.sh Certificate Transparency API for subdomain discovery."""

import requests
from app.config import settings


class CRTService:
    name = "crt_sh"
    rate_limit = settings.CRT_RATE_LIMIT

    def query(self, domain: str) -> list[dict]:
        url = f"https://crt.sh/?q={domain}&output=json"
        try:
            resp = requests.get(
                url, timeout=30, headers={"User-Agent": "OSINT-Dashboard/1.0"}
            )
            resp.raise_for_status()
            data = resp.json()

            seen = set()
            results = []
            for entry in data:
                # crt.sh name_values is pipe-separated in some responses
                raw = entry.get("name_value", "") or ""
                alts = entry.get("name_values", []) or []
                names = list(set([raw] + alts) - {""})
                for alt in names:
                    if alt not in seen and (
                        alt == domain or alt.endswith("." + domain)
                    ):
                        seen.add(alt)
                        results.append(
                            {
                                "type": "subdomain",
                                "value": alt,
                                "extra": f'{{"cert_issuer": "{entry.get("issuer_ca_id", "")}"}}',
                            }
                        )
            return results
        except requests.RequestException as e:
            return [{"type": "error", "value": f"CRT.sh request failed: {e}"}]
