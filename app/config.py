"""Application configuration via pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # === API Keys ===
    SHODAN_API_KEY: str = ""
    VIRUSTOTAL_API_KEY: str = ""

    # === Service toggles ===
    SHODAN_ENABLED: bool = True
    VIRUSTOTAL_ENABLED: bool = True
    CRT_ENABLED: bool = True
    WHOIS_ENABLED: bool = True
    DNS_ENABLED: bool = True

    # === Rate Limits (req/min) ===
    SHODAN_RATE_LIMIT: int = 1
    VIRUSTOTAL_RATE_LIMIT: int = 4
    CRT_RATE_LIMIT: int = 10
    WHOIS_RATE_LIMIT: int = 2
    DNS_RATE_LIMIT: int = 20

    # === Recursion ===
    MAX_RECURSION_DEPTH: int = 2
    MAX_RECURSIVE_TARGETS: int = 25

    # === Retention ===
    DATA_RETENTION_DAYS: int = 90
    RETENTION_DAYS: int = 90  # .env compatibility alias
    BACKUP_DIR: str = "/ai-bunker/osint-dashboard/backups"

    # === Server ===
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # === Celery ===
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"
    CELERY_WORKER_CONCURRENCY: int = 4
    CELERY_TASK_TIMEOUT: int = 300

    # === App ===
    DATABASE_URL: str = "sqlite:///./data/osint.db"
    SECRET_KEY: str = "change-this-in-production"
    DEBUG: bool = True

    model_config = {"extra": "ignore"}


settings = Settings()
