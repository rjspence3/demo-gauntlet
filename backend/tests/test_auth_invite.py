"""
Tests for beta invite code authentication.
"""
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from backend.main import app
from backend.database import get_session
from backend.config import config
from backend.models.db_models import User # Explicit import
from unittest.mock import patch

import os
# Setup file-based DB for tests to avoid in-memory threading issues
TEST_DB = "test_auth.db"
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)

engine = create_engine(
    f"sqlite:///{TEST_DB}",
    connect_args={"check_same_thread": False},
)

def get_test_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture():
    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

@pytest.fixture(name="session")
def session_fixture():
    with Session(engine) as session:
        yield session

def test_login_with_code_success(client: TestClient, session: Session):
    """Test login with correct code succeeds and creates guest user."""
    with patch.object(config, 'BETA_INVITE_CODE', "secret123"):
        response = client.post(
            "/auth/login-with-code",
            json={"invite_code": "secret123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        
        # Verify guest user created
        user = session.exec(select(User).where(User.email == "guest@demo.com")).first()
        assert user is not None

def test_login_with_code_failure(client: TestClient, session: Session):
    """Test login with incorrect code fails."""
    with patch.object(config, 'BETA_INVITE_CODE', "secret123"):
        response = client.post(
            "/auth/login-with-code",
            json={"invite_code": "wrong"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid invite code"
