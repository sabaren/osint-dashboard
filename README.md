# OSINT Domain Scanning Dashboard

A domain reconnaissance tool for your local network. It queries free OSINT APIs and gives you a visual breakdown of what's out there for each domain you scan.

## What it does

- Queries 5 sources: Shodan, CRT.sh, WHOIS, VirusTotal, Google DNS
- Follows subdomains recursively (stops at 2 levels)
- Batch scanning — throw multiple domains at once
- Live progress updates via HTMX (no page reloads)
- Charts: doughnut, bar, and timeline views powered by Chart.js
- Export to CSV, JSON, Markdown, or styled PDF (WeasyPrint)
- Keeps data for 90 days, with weekly JSON backups
- Mobile-responsive, Tailwind CSS

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Nginx (reverse proxy :80)                          │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│  FastAPI (HTMX + Jinja2 + Tailwind CDN)             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Scans    │  │ Dashboard│  │ Export   │           │
│  │ Router   │  │ Router   │  │ Router   │           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
│       │              │              │               │
│  ┌────▼──────────────▼──────────────▼───────┐       │
│  │  Services Layer                          │       │
│  │  Shodan │ CRT.sh │ WHOIS │ VT │ DNS      │       │
│  └──────────────────────────────────────────┘       │
└─────────────────────┬───────────────────────────────┘
                      │ Celery tasks
┌─────────────────────▼───────────────────────────────┐
│  Celery Worker + Beat  │  Redis  │  SQLite          │
└─────────────────────────────────────────────────────┘
```

## Quick start

### Prerequisites

- Docker + Docker Compose
- API keys for [Shodan](https://account.shodan.io/) and [VirusTotal](https://www.virustotal.com/gui/my-apikey) (optional — the dashboard works without them)

### Setup

```bash
# 1. Clone and configure
cp .env.example .env
nano .env  # Fill in your API keys

# 2. Build and start
make up

# 3. Open the dashboard
open http://localhost
```

### Makefile commands

| Command | What it does |
|---|---|
| `make up` | Build and start all services |
| `make down` | Stop everything |
| `make logs` | Follow web service logs |
| `make test` | Run pytest |
| `make lint` | Run Ruff |
| `make format` | Run Black |
| `make backup` | Trigger a manual JSON backup |
| `make clean` | Remove containers, images, volumes |

## Configuration

Edit `.env` after copying from `.env.example`:

```ini
# API Keys — optional but recommended
SHODAN_API_KEY=your_key_here
VIRUSTOTAL_API_KEY=your_key_here

# Rate limits (requests/min)
SHODAN_RATE_LIMIT=1
VIRUSTOTAL_RATE_LIMIT=4
CRT_RATE_LIMIT=10

# How deep to recurse on subdomains
MAX_RECURSION_DEPTH=2

# Data retention
RETENTION_DAYS=90
BACKUP_DIR=/path/to/backups
```

## Deployment

Run it on any machine with Docker:

```bash
cd /path/to/osint-dashboard
make up -d

# Open from any LAN device
# http://<server-ip>
```

### Things to keep in mind

- **Auth:** This was built for LAN-only use. If you expose it externally, add authentication first.
- **Database:** SQLite is fine for a single user. Switch to PostgreSQL if multiple people will be running scans at once.
- **Backups:** Celery Beat handles weekly JSON exports automatically.
- **Rate limits:** Tweak the `.env` values based on your API tier.

## Project structure

```
osint-dashboard/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Pydantic settings
│   ├── database.py          # SQLAlchemy engine
│   ├── models.py            # ORM models
│   ├── celery_app.py        # Celery tasks + Beat schedule
│   ├── routers/             # API routes
│   │   ├── scans.py         # Scan management
│   │   ├── dashboard.py     # Dashboard UI
│   │   └── export.py        # CSV/JSON/MD/PDF export
│   ├── services/            # OSINT API clients
│   │   ├── shodan_service.py
│   │   ├── crt_service.py
│   │   ├── whois_service.py
│   │   ├── virustotal_service.py
│   │   └── dns_service.py
│   ├── templates/           # Jinja2 + HTMX templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── batch.html
│   │   ├── scan_results.html
│   │   └── scan_pdf.html
│   └── static/              # CSS + JS
│       ├── css/style.css
│       └── js/charts.js
├── nginx/nginx.conf         # Reverse proxy
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── .env.example
├── .gitignore
└── tests/
    ├── __init__.py
    └── test_main.py
```

## License

MIT — [Nicholaus Sabare](https://github.com/sabaren)
