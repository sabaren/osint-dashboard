"""Pytest fixtures for testing with an in-memory SQLite database."""

import os
import tempfile

import pytest

# Set test DB URL BEFORE any app imports so settings picks it up
_test_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_test_db_file}")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def test_db():
    """Create tables in the test database for the session."""
    from sqlalchemy import create_engine
    from app.database import Base

    engine = create_engine(os.environ["DATABASE_URL"], echo=False)
    Base.metadata.create_all(engine)
    return engine


def pytest_configure(config):
    """Create test DB tables before any tests run."""
    from sqlalchemy import create_engine
    from app.database import Base

    engine = create_engine(os.environ["DATABASE_URL"], echo=False)
    Base.metadata.create_all(engine)


@pytest.fixture(scope="session")
def client(test_db):
    """FastAPI test client with test database."""
    with TestClient(app) as c:
        yield c
