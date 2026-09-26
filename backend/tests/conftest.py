"""
Pytest configuration and shared fixtures.
Uses SQLite in-memory DB — no MySQL needed for tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# In-memory SQLite — no file, no lock issues
SQLITE_URL = "sqlite://"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Share same connection across threads
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Create all tables once for the whole test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_client(client):
    """TestClient with a registered+logged-in user's JWT token."""
    # Try register first
    reg = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "TestPass@123",
        "confirm_password": "TestPass@123",
    })
    if reg.status_code == 201:
        token = reg.json()["access_token"]
    else:
        # Already registered — login instead
        login = client.post("/api/auth/login", json={
            "email": "testuser@example.com",
            "password": "TestPass@123",
        })
        token = login.json()["access_token"]

    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
