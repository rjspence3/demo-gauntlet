import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.main import app
from backend.api.deps import get_current_user
from backend.models.db_models import User
from sqlmodel import create_engine, SQLModel
from sqlalchemy.pool import StaticPool

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
    # StaticPool keeps a single shared connection so every thread sees the same
    # in-memory DB; without it, async endpoints doing DB work in a worker thread
    # get a fresh empty database ("no such table: sessions").
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with patch("backend.database.engine", engine):
        yield engine

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """
    Reset the slowapi limiter before each test. All tests share the same
    'testclient' IP, so without this the 5/min counts bleed across tests and
    make rate-limit assertions order-dependent.
    """
    from backend.limiter import limiter
    limiter.reset()
    yield


@pytest.fixture(autouse=True)
def mock_arq_pool():
    """
    Mock the arq Redis pool so tests don't require a live Redis connection.
    """
    mock_pool = MagicMock()
    mock_pool.enqueue_job = AsyncMock(return_value=None)
    app.state.arq_pool = mock_pool
    app.state.arq_queue_name = "test_queue"
    yield mock_pool
    # Clean up app state after each test
    if hasattr(app.state, "arq_pool"):
        del app.state.arq_pool
    if hasattr(app.state, "arq_queue_name"):
        del app.state.arq_queue_name
