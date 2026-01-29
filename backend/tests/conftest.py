import pytest
from backend.main import app
from backend.api.deps import get_current_user
from backend.models.db_models import User

from sqlmodel import create_engine, SQLModel
from unittest.mock import patch

@pytest.fixture(autouse=True)
def override_auth():
    """
    Override the get_current_user dependency for all tests.
    """
    mock_user = User(id=1, email="test@example.com", hashed_password="fake", is_active=True)
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides = {}

@pytest.fixture(autouse=True)
def mock_db_engine():
    """
    Mock the database engine with an in-memory SQLite database.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with patch("backend.database.engine", engine):
        yield engine
