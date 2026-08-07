"""SQLAlchemy models for scans and results."""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, index=True)
    status = Column(
        String(20), default="pending"
    )  # pending, running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    results = relationship(
        "ScanResult", back_populates="scan", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("idx_scan_domain_status", "domain", "status"),)


class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    source = Column(String(50), nullable=False)  # shodan, crt, whois, virustotal, dns
    target = Column(String(255), nullable=False)
    data_type = Column(String(50))  # port, subdomain, email, record, threat
    value = Column(Text)
    extra = Column(Text)  # JSON blob for extra metadata
    detected_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("Scan", back_populates="results")

    __table_args__ = (Index("idx_result_scan_source", "scan_id", "source"),)
