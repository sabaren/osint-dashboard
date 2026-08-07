# OSINT Intelligence Dashboard

Professional, LAN-only domain reconnaissance dashboard visualizing attack surface data across multiple free-tier OSINT APIs.

## Features

- **5 Data Sources**: Shodan, CRT.sh, WHOIS, VirusTotal, Google DNS
- **Recursive Subdomain Discovery** (2-level depth cap)
- **Batch Scanning** — scan multiple domains simultaneously
- **Real-time Progress** — HTMX-powered live scan status updates
- **Interactive Visualizations** — Chart.js doughnut, bar, and timeline charts
- **4 Export Formats** — CSV, JSON, Markdown, Styled PDF (via WeasyPrint)
- **90-Day Data Retention** with automatic weekly JSON backups
- **Dark-mode UI** — Tailwind CSS, mobile-responsive

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

## Quick Start

### Prerequisites

- Docker + Docker Compose
- API keys for [Shodan](https://account.shodan.io/) and [VirusTotal](https://www.virustotal.com/gui/my-apikey) (optional)

### Setup

```bash
# 1. Clone and configure
cp .env.example .env
nano .env  # Fill in your API keys

# 2. Build and start
make up

# 3. Access the dashboard
open http://localhost
```

### Makefile Commands

| Command | Description |
|---|---|
| `make up` | Build and start all services |
| `make down` | Stop all containers |
| `make logs` | Follow web service logs |
| `make test` | Run pytest |
| `make lint` | Run Ruff linter |
| `make format` | Run Black formatter |
| `make backup` | Trigger manual JSON backup |
| `make clean` | Remove containers, images, volumes |

## Configuration

Edit `.env` to customize:

```ini
# API Keys
SHODAN_API_KEY=your_key_here
VIRUSTOTAL_API_KEY=your_key_here

# Rate Limits (requests/min)
SHODAN_RATE_LIMIT=1
VIRUSTOTAL_RATE_LIMIT=4
CRT_RATE_LIMIT=10

# Recursion
MAX_RECURSION_DEPTH=2

# Retention
RETENTION_DAYS=90
BACKUP_DIR=/path/to/backups
```

## Deployment

### Deployment

```bash
cd /path/to/osint-dashboard
make up -d

# Access from any LAN machine
# http://<your-server-ip>
```

### Production Considerations

- **Auth**: The dashboard assumes LAN trust. Add authentication if exposing externally.
- **Database**: SQLite works for single-user. Migrate to PostgreSQL for multi-user.
- **Backups**: Weekly JSON exports are scheduled via Celery Beat.
- **Rate Limits**: Adjust `.env` limits based on your API tier.

## Project Structure

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

MIT © [Nicholaus Sabare](https://github.com/sabaren)
