"""DNS lookup service using dnspython for DNS record enumeration."""

import dns.resolver
from app.config import settings


class DNSService:
    name = "dns"
    rate_limit = settings.DNS_RATE_LIMIT

    RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "SRV"]

    def query(self, domain: str) -> list[dict]:
        results = []
        resolver = dns.resolver.Resolver()
        resolver.timeout = 10
        resolver.lifetime = 10

        for rtype in self.RECORD_TYPES:
            try:
                answers = resolver.resolve(domain, rtype)
                for rdata in answers:
                    value = str(rdata).strip().rstrip(".")
                    results.append({
                        "type": f"dns_{rtype.lower()}",
                        "value": value,
                        "extra": f'{{"ttl": {answers.rrset.ttl}}}',
                    })
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
                pass
            except Exception:
                pass

        if not results:
            return [{"type": "dns_info", "value": "No DNS records found or all queries timed out"}]
        return results
